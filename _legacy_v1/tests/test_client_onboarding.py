# tests/test_client_onboarding.py

import pytest
from unittest.mock import MagicMock, patch

# El objetivo de este test es simular el flujo de onboarding sin 
# depender de sistemas externos como APIs de pago o servidores de correo.

# Suponemos que tenemos una clase o módulo que maneja el onboarding
class ClientOnboarder:
    def __init__(self, license_api, auth_system, mailer):
        self.license_api = license_api
        self.auth_system = auth_system
        self.mailer = mailer

    def onboard_new_client(self, client_name, admin_email, license_type):
        print(f"Onboarding {client_name}")
        # 1. Generar y registrar licencia
        license_key = self.license_api.create_license(client_name, license_type)
        if not license_key:
            raise Exception("Failed to create license")
        
        # 2. Crear cuenta de admin
        user_created = self.auth_system.create_admin_user(client_name, admin_email)
        if not user_created:
            raise Exception("Failed to create admin user")

        # 3. Enviar correo
        self.mailer.send_welcome_email(admin_email, license_key)
        return True

@pytest.fixture
def mock_systems():
    """Crea mocks para todos los sistemas externos."""
    mock_license_api = MagicMock()
    mock_license_api.create_license.return_value = "MOCK-LICENSE-KEY-123"
    
    mock_auth_system = MagicMock()
    mock_auth_system.create_admin_user.return_value = True
    
    mock_mailer = MagicMock()
    
    return mock_license_api, mock_auth_system, mock_mailer

def test_successful_onboarding_flow(mock_systems):
    """Prueba un flujo de onboarding exitoso de principio a fin."""
    mock_license_api, mock_auth_system, mock_mailer = mock_systems
    
    onboarder = ClientOnboarder(mock_license_api, mock_auth_system, mock_mailer)
    
    client_name = "TestCorp"
    admin_email = "admin@testcorp.com"
    license_type = "Enterprise SaaS"
    
    result = onboarder.onboard_new_client(client_name, admin_email, license_type)
    
    # Verificar que el resultado es exitoso
    assert result is True
    
    # Verificar que se llamó a cada sistema mockeado con los argumentos correctos
    mock_license_api.create_license.assert_called_once_with(client_name, license_type)
    mock_auth_system.create_admin_user.assert_called_once_with(client_name, admin_email)
    mock_mailer.send_welcome_email.assert_called_once_with(admin_email, "MOCK-LICENSE-KEY-123")

def test_onboarding_fails_if_license_creation_fails(mock_systems):
    """Verifica que el proceso se detiene si la API de licencias falla."""
    mock_license_api, mock_auth_system, mock_mailer = mock_systems
    
    # Simular fallo en la creación de la licencia
    mock_license_api.create_license.return_value = None
    
    onboarder = ClientOnboarder(mock_license_api, mock_auth_system, mock_mailer)
    
    with pytest.raises(Exception, match="Failed to create license"):
        onboarder.onboard_new_client("FailCorp", "admin@failcorp.com", "On-Premise")
    
    # Asegurarse de que no se intentó crear un usuario o enviar un correo
    mock_auth_system.create_admin_user.assert_not_called()
    mock_mailer.send_welcome_email.assert_not_called()
