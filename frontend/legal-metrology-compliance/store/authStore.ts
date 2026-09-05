import type { LoginResponse } from "../types/auth";

let currentSession: LoginResponse | null = null;

export const authStore = {
  getSession() {
    return currentSession;
  },

  setSession(session: LoginResponse) {
    currentSession = session;
  },

  clearSession() {
    currentSession = null;
  },
};
