export type UserRole = "admin" | "asesor";

export type ManagedUser = {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  phone: string;
  role: UserRole;
  is_active: boolean;
  deactivation_reason: string;
  failed_attempts: number;
  is_locked: boolean;
  date_joined: string;
};

export type ManagedUserInput = Pick<
  ManagedUser,
  "email" | "first_name" | "last_name" | "phone" | "role"
>;
