export interface Token {
  access_token: string;
  token_type: string;
}

export interface TokenData {
  username?: string;
}

export interface UserBase {
  username: string;
  email: string;
}

export interface UserCreate extends UserBase {
  password: string;
}

export interface User extends UserBase {
  id: number;
  role_id?: number;
}

export interface QueryRequest {
  text: string;
}

export interface QueryResponse {
  responses: string[];
  status?: string;
}
