import * as SecureStore from "expo-secure-store";

import { API_BASE_URL } from "../constants/config";


export interface LoginResponse {
  access_token: string;
  token_type: string;
  officer_id: string;
  role: string;
}

export interface Officer {
  id: number;
  officer_id: string;
  full_name: string;
  email: string;
  role: string;
  is_active: boolean;
}


export async function loginOfficer(
  officer_id: string,
  password: string
): Promise<LoginResponse> {
  try {
    const response = await fetch(
      `${API_BASE_URL}/auth/login`,
      {
        method: "POST",

        headers: {
          "Content-Type": "application/json",
        },

        body: JSON.stringify({
          officer_id,
          password,
        }),
      }
    );

    const data = await response.json();

    if (!response.ok) {
      throw new Error(
        data.detail || "Invalid Officer ID or password"
      );
    }

    return data;
  } catch (error: any) {
    console.error("Login API Error:", error);

    if (error.message) {
      throw error;
    }

    throw new Error(
      "Unable to connect to the server."
    );
  }
}


export async function getAccessToken(): Promise<
  string | null
> {
  return await SecureStore.getItemAsync(
    "access_token"
  );
}


async function authenticatedFetch(
  endpoint: string,
  options: RequestInit = {}
) {
  const token =
    await SecureStore.getItemAsync(
      "access_token"
    );

  if (!token) {
    throw new Error(
      "Authentication token not found."
    );
  }

  const response = await fetch(
    `${API_BASE_URL}${endpoint}`,
    {
      ...options,

      headers: {
        "Content-Type": "application/json",

        ...(options.headers || {}),

        Authorization: `Bearer ${token}`,
      },
    }
  );

  return response;
}


export async function getCurrentOfficer(): Promise<Officer> {
  try {
    const response =
      await authenticatedFetch(
        "/auth/me",
        {
          method: "GET",
        }
      );

    const data = await response.json();


    if (response.status === 401) {
      await logoutOfficer();

      throw new Error(
        "Your session has expired. Please login again."
      );
    }

    if (!response.ok) {
      throw new Error(
        data.detail ||
          "Unable to fetch officer information."
      );
    }

    return data;
  } catch (error: any) {
    console.error(
      "Get Current Officer Error:",
      error
    );

    throw error;
  }
}

export async function logoutOfficer() {
  await SecureStore.deleteItemAsync(
    "access_token"
  );

  await SecureStore.deleteItemAsync(
    "officer_id"
  );

  await SecureStore.deleteItemAsync(
    "role"
  );
}