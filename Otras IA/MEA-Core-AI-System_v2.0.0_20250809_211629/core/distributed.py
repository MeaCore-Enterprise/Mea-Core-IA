"""
MEA-Core Distributed Computing System
Lightweight distributed inference farm for local AI processing
"""

import json
import time
import threading
import logging
import socket
import hashlib
import platform
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import queue
import multiprocessing as mp

try:
    import psutil
except ImportError:
    psutil = None
    logging.warning("psutil not available - system monitoring will be limited")

class TaskType(Enum):
    OCR = "ocr"
    BM25_INDEX = "bm25_index"
    EMBEDDINGS = "embeddings" 
    CLASSIFY = "classify"
    SUMMARIZE = "summarize"
    STT = "stt"
    TTS = "tts"

class WorkerStatus(Enum):
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"

@dataclass
class WorkerCapabilities:
    cpu_cores: int
    gpu_count: int
    gpu_memory: int  # MB
    system_memory: int  # MB
    supported_tasks: List[str]
    compute_score: float
    network_speed: float  # Mbps estimate

@dataclass  
class Task:
    id: str
    type: TaskType
    data: Dict[str, Any]
    priority: int = 0
    estimated_time: float = 1.0  # seconds
    required_memory: int = 128  # MB
    gpu_preferred: bool = False
    created_at: float = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = time.time()

@dataclass
class WorkerInfo:
    worker_id: str
    host: str
    port: int
    status: WorkerStatus
    capabilities: WorkerCapabilities
    current_task: Optional[str] = None
    last_heartbeat: float = 0
    load_average: float = 0.0

class DistributedScheduler:
    """Lightweight distributed task scheduler inspired by render farms"""
    
    def __init__(self, port: int = 8765):
        self.port = port
        self.workers: Dict[str, WorkerInfo] = {}
        self.task_queue = queue.PriorityQueue()
        self.running_tasks: Dict[str, Task] = {}
        self.completed_tasks: Dict[str, Any] = {}
        self.failed_tasks: Dict[str, str] = {}
        self.lock = threading.Lock()
        self.running = False
        
        # Configuration
        self.heartbeat_timeout = 30.0  # seconds
        self.max_retries = 2
        self.discovery_interval = 10.0
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def start(self):
        """Start the scheduler"""
        self.running = True
        self.logger.info(f"Starting MEA-Core distributed scheduler on port {self.port}")
        
        # Start background threads
        threading.Thread(target=self._heartbeat_monitor, daemon=True).start()
        threading.Thread(target=self._task_dispatcher, daemon=True).start()
        threading.Thread(target=self._worker_discovery, daemon=True).start()
        
    def stop(self):
        """Stop the scheduler"""
        self.running = False
        self.logger.info("Stopping MEA-Core distributed scheduler")
        
    def register_worker(self, worker_info: WorkerInfo) -> bool:
        """Register a new worker"""
        with self.lock:
            worker_info.last_heartbeat = time.time()
            self.workers[worker_info.worker_id] = worker_info
            
        self.logger.info(f"Registered worker {worker_info.worker_id} with {worker_info.capabilities.cpu_cores} cores")
        return True
        
    def submit_task(self, task: Task) -> str:
        """Submit a task for processing"""
        task.id = self._generate_task_id(task)
        
        # Calculate priority score (lower = higher priority)
        priority_score = -task.priority + task.estimated_time
        
        self.task_queue.put((priority_score, time.time(), task))
        self.logger.info(f"Submitted task {task.id} of type {task.type.value}")
        
        return task.id
        
    def get_task_result(self, task_id: str) -> Optional[Any]:
        """Get the result of a completed task"""
        return self.completed_tasks.get(task_id)
        
    def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        with self.lock:
            active_workers = sum(1 for w in self.workers.values() if w.status != WorkerStatus.OFFLINE)
            
            return {
                "workers": {
                    "total": len(self.workers),
                    "active": active_workers,
                    "idle": sum(1 for w in self.workers.values() if w.status == WorkerStatus.IDLE),
                    "busy": sum(1 for w in self.workers.values() if w.status == WorkerStatus.BUSY),
                },
                "tasks": {
                    "queued": self.task_queue.qsize(),
                    "running": len(self.running_tasks),
                    "completed": len(self.completed_tasks),
                    "failed": len(self.failed_tasks),
                },
                "compute_capacity": {
                    "total_cores": sum(w.capabilities.cpu_cores for w in self.workers.values()),
                    "total_gpu_memory": sum(w.capabilities.gpu_memory for w in self.workers.values()),
                    "avg_load": sum(w.load_average for w in self.workers.values()) / max(len(self.workers), 1),
                }
            }
    
    def _generate_task_id(self, task: Task) -> str:
        """Generate unique task ID"""
        content = f"{task.type.value}_{time.time()}_{task.data}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
        
    def _heartbeat_monitor(self):
        """Monitor worker heartbeats"""
        while self.running:
            current_time = time.time()
            
            with self.lock:
                offline_workers = []
                for worker_id, worker in self.workers.items():
                    if current_time - worker.last_heartbeat > self.heartbeat_timeout:
                        worker.status = WorkerStatus.OFFLINE
                        offline_workers.append(worker_id)
                        
                        # Reschedule any tasks from offline workers
                        if worker.current_task:
                            self._reschedule_task(worker.current_task)
                            
                for worker_id in offline_workers:
                    self.logger.warning(f"Worker {worker_id} went offline")
                    
            time.sleep(self.heartbeat_timeout / 3)
            
    def _task_dispatcher(self):
        """Dispatch tasks to available workers"""
        while self.running:
            try:
                # Get next task from queue (blocks until available)
                priority, timestamp, task = self.task_queue.get(timeout=1.0)
                
                # Find best worker for this task
                worker = self._find_best_worker(task)
                if worker:
                    self._assign_task(worker, task)
                else:
                    # No suitable worker available, requeue
                    self.task_queue.put((priority, timestamp, task))
                    time.sleep(0.5)
                    
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Error in task dispatcher: {e}")
                
    def _worker_discovery(self):
        """Discover workers on the local network"""
        while self.running:
            try:
                # Simple UDP broadcast for worker discovery
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                sock.settimeout(2.0)
                
                discovery_msg = json.dumps({
                    "type": "discovery",
                    "scheduler_port": self.port,
                    "timestamp": time.time()
                }).encode()
                
                sock.sendto(discovery_msg, ('<broadcast>', 8766))
                sock.close()
                
            except Exception as e:
                self.logger.debug(f"Worker discovery error: {e}")
                
            time.sleep(self.discovery_interval)
            
    def _find_best_worker(self, task: Task) -> Optional[WorkerInfo]:
        """Find the best worker for a task using simple scheduling policy"""
        with self.lock:
            available_workers = [
                w for w in self.workers.values() 
                if w.status == WorkerStatus.IDLE and 
                   task.type.value in w.capabilities.supported_tasks
            ]
            
            if not available_workers:
                return None
                
            # Score workers: (compute_score * gpu_preference + memory_fit) / load
            def worker_score(worker: WorkerInfo) -> float:
                gpu_bonus = 1.5 if task.gpu_preferred and worker.capabilities.gpu_count > 0 else 1.0
                memory_fit = min(worker.capabilities.system_memory / max(task.required_memory, 1), 2.0)
                load_penalty = max(worker.load_average, 0.1)
                
                return (worker.capabilities.compute_score * gpu_bonus * memory_fit) / load_penalty
                
            return max(available_workers, key=worker_score)
            
    def _assign_task(self, worker: WorkerInfo, task: Task):
        """Assign a task to a worker"""
        with self.lock:
            worker.status = WorkerStatus.BUSY  
            worker.current_task = task.id
            self.running_tasks[task.id] = task
            
        self.logger.info(f"Assigned task {task.id} to worker {worker.worker_id}")
        
        # Here you would send the task to the actual worker
        # For now, we'll simulate task completion
        threading.Thread(
            target=self._simulate_task_execution, 
            args=(worker, task), 
            daemon=True
        ).start()
        
    def _simulate_task_execution(self, worker: WorkerInfo, task: Task):
        """Simulate task execution (replace with actual RPC call)"""
        try:
            # Simulate processing time
            processing_time = task.estimated_time + (task.estimated_time * 0.2 * worker.load_average)
            time.sleep(min(processing_time, 5.0))  # Cap simulation time
            
            # Simulate successful completion
            result = {
                "task_id": task.id,
                "result": f"Processed {task.type.value} successfully",
                "processing_time": processing_time,
                "worker_id": worker.worker_id
            }
            
            with self.lock:
                self.completed_tasks[task.id] = result
                if task.id in self.running_tasks:
                    del self.running_tasks[task.id]
                    
                worker.status = WorkerStatus.IDLE
                worker.current_task = None
                
            self.logger.info(f"Task {task.id} completed by worker {worker.worker_id}")
            
        except Exception as e:
            self.logger.error(f"Task {task.id} failed on worker {worker.worker_id}: {e}")
            
            with self.lock:
                self.failed_tasks[task.id] = str(e)
                if task.id in self.running_tasks:
                    del self.running_tasks[task.id]
                    
                worker.status = WorkerStatus.ERROR
                worker.current_task = None
                
    def _reschedule_task(self, task_id: str):
        """Reschedule a failed task"""
        if task_id in self.running_tasks:
            task = self.running_tasks[task_id]
            del self.running_tasks[task_id]
            
            # Resubmit with lower priority
            task.priority -= 1
            priority_score = -task.priority + task.estimated_time
            self.task_queue.put((priority_score, time.time(), task))
            
            self.logger.info(f"Rescheduled task {task_id}")

class LocalWorker:
    """Local worker that can process tasks"""
    
    def __init__(self, worker_id: str = None, scheduler_host: str = "localhost", scheduler_port: int = 8765):
        self.worker_id = worker_id or self._generate_worker_id()
        self.scheduler_host = scheduler_host
        self.scheduler_port = scheduler_port
        self.capabilities = self._detect_capabilities()
        self.status = WorkerStatus.IDLE
        self.running = False
        
        self.logger = logging.getLogger(__name__)
        
    def _generate_worker_id(self) -> str:
        """Generate unique worker ID"""
        hostname = platform.node()
        if psutil:
            boot_time = psutil.boot_time()
            mac = ':'.join(['{:02x}'.format((int(boot_time) >> ele) & 0xff) for ele in range(8, -1, -1)])
        else:
            # Fallback to timestamp-based ID
            mac = str(int(time.time()) % 1000000)
        return hashlib.md5(f"{hostname}_{mac}".encode()).hexdigest()[:12]
        
    def _detect_capabilities(self) -> WorkerCapabilities:
        """Detect system capabilities"""
        if psutil:
            cpu_cores = psutil.cpu_count(logical=True)
            memory = psutil.virtual_memory().total // (1024 * 1024)  # MB
        else:
            cpu_cores = mp.cpu_count()
            memory = 4096  # Default 4GB assumption
        
        # Simple GPU detection (would need more sophisticated detection in real implementation)
        gpu_count = 0
        gpu_memory = 0
        
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            gpu_count = len(gpus)
            gpu_memory = sum(gpu.memoryTotal for gpu in gpus) if gpus else 0
        except ImportError:
            pass
            
        # Calculate compute score based on hardware
        compute_score = cpu_cores * 1.0 + (gpu_count * 2.0) + (memory / 1000)
        
        supported_tasks = [
            TaskType.OCR.value,
            TaskType.BM25_INDEX.value, 
            TaskType.CLASSIFY.value,
            TaskType.SUMMARIZE.value
        ]
        
        # Add GPU-dependent tasks if available
        if gpu_count > 0:
            supported_tasks.extend([
                TaskType.EMBEDDINGS.value,
                TaskType.STT.value,
                TaskType.TTS.value
            ])
            
        return WorkerCapabilities(
            cpu_cores=cpu_cores,
            gpu_count=gpu_count,
            gpu_memory=gpu_memory,
            system_memory=memory,
            supported_tasks=supported_tasks,
            compute_score=compute_score,
            network_speed=100.0  # Assume 100 Mbps for now
        )
        
    def start(self):
        """Start the worker"""
        self.running = True
        self.logger.info(f"Starting MEA-Core worker {self.worker_id}")
        
        # Register with scheduler
        self._register_with_scheduler()
        
        # Start heartbeat
        threading.Thread(target=self._heartbeat_loop, daemon=True).start()
        
    def stop(self):
        """Stop the worker"""
        self.running = False
        self.logger.info(f"Stopping MEA-Core worker {self.worker_id}")
        
    def _register_with_scheduler(self):
        """Register this worker with the scheduler"""
        worker_info = WorkerInfo(
            worker_id=self.worker_id,
            host=socket.gethostbyname(socket.gethostname()),
            port=8767,  # Worker listening port
            status=WorkerStatus.IDLE,
            capabilities=self.capabilities
        )
        
        # In a real implementation, this would be an RPC call
        self.logger.info(f"Registering worker with scheduler at {self.scheduler_host}:{self.scheduler_port}")
        
    def _heartbeat_loop(self):
        """Send periodic heartbeats to scheduler"""
        while self.running:
            try:
                # Update load average
                load_avg = psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else psutil.cpu_percent() / 100.0
                
                # In real implementation, send heartbeat to scheduler
                self.logger.debug(f"Heartbeat: load={load_avg:.2f}")
                
            except Exception as e:
                self.logger.error(f"Heartbeat error: {e}")
                
            time.sleep(10.0)  # Heartbeat every 10 seconds

# Global scheduler instance
_scheduler_instance = None

def get_distributed_scheduler(port: int = 8765) -> DistributedScheduler:
    """Get or create the global distributed scheduler instance"""
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = DistributedScheduler(port)
    return _scheduler_instance

def create_distributed_task(task_type: str, data: Dict[str, Any], **kwargs) -> Task:
    """Helper function to create distributed tasks"""
    try:
        task_enum = TaskType(task_type)
    except ValueError:
        raise ValueError(f"Unknown task type: {task_type}")
        
    return Task(
        id="",  # Will be generated by scheduler
        type=task_enum,
        data=data,
        **kwargs
    )