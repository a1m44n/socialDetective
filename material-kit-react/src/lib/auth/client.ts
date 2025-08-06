'use client';

import type { User } from '@/types/user';

function generateToken(): string {
  const arr = new Uint8Array(12);
  window.crypto.getRandomValues(arr);
  return Array.from(arr, (v) => v.toString(16).padStart(2, '0')).join('');
}

const user = {
  id: 'USR-000',
  avatar: '/assets/avatar.png',
  firstName: 'Sofia',
  lastName: 'Rivers',
  email: 'sofia@devias.io',
} satisfies User;

export interface SignUpParams {
  firstName: string;
  lastName: string;
  email: string;
  password: string;
}

export interface SignInWithOAuthParams {
  provider: 'google' | 'discord';
}

export interface SignInWithPasswordParams {
  email: string;
  password: string;
  role: string;
}

export interface ResetPasswordParams {
  email: string;
}

class AuthClient {
  private baseUrl = `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/auth`;

  async signUp(_: SignUpParams): Promise<{ error?: string }> {
    // Make API request

    // We do not handle the API, so we'll just generate a token and store it in localStorage.
    const token = generateToken();
    localStorage.setItem('custom-auth-token', token);

    return {};
  }

  async signInWithOAuth(_: SignInWithOAuthParams): Promise<{ error?: string }> {
    return { error: 'Social authentication not implemented' };
  }

  async signInWithPassword(params: SignInWithPasswordParams): Promise<{ error?: string }> {
    try {
      console.log('Attempting login with params:', { ...params, password: '***' });
      console.log('Making request to:', `${this.baseUrl}/login/`);

      const response = await fetch(`${this.baseUrl}/login/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(params),
      });

      console.log('Response status:', response.status);
      const data = await response.json();
      console.log('Response data:', data);

      if (!response.ok) {
        console.error('Login failed:', data.error || 'Invalid credentials');
        return { error: data.error || 'Invalid credentials' };
      }

      // Store the token
      if (data.token) {
        console.log('Login successful, storing token');
        localStorage.setItem('auth-token', data.token);
      }

      return {};
    } catch (error) {
      console.error('Login error:', error);
      return { error: 'Failed to connect to server' };
    }
  }

  async resetPassword(_: ResetPasswordParams): Promise<{ error?: string }> {
    return { error: 'Password reset not implemented' };
  }

  async updatePassword(_: ResetPasswordParams): Promise<{ error?: string }> {
    return { error: 'Update reset not implemented' };
  }

  async getUser(): Promise<{ data?: User | null; error?: string }> {
    try {
      const token = localStorage.getItem('auth-token');
      if (!token) {
        return { data: null };
      }

      const response = await fetch(`${this.baseUrl}/validate/`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        localStorage.removeItem('auth-token');
        return { data: null };
      }

      const data = await response.json();
      return { data: data.user };
    } catch (error) {
      console.error('Get user error:', error);
      return { data: null };
    }
  }

  async signOut(): Promise<{ error?: string }> {
    localStorage.removeItem('auth-token');
    return {};
  }
}

export const authClient = new AuthClient();
