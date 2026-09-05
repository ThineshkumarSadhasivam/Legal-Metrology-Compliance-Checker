export type LoginRequest = {
  officer_id: string;
  password: string;
};

export type LoginResponse = {
  access_token: string;
  token_type: string;
  officer_id: string;
  role: string;
};
