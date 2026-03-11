import NextAuth from 'next-auth';
import CredentialsProvider from 'next-auth/providers/credentials';
import { createHash } from 'crypto';

function hashPassword(password: string): string {
  return createHash('sha256').update(password).digest('hex');
}

const handler = NextAuth({
  providers: [
    CredentialsProvider({
      name: 'Credentials',
      credentials: {
        username: { label: 'Username', type: 'text', placeholder: 'admin' },
        password: { label: 'Password', type: 'password' },
      },
      async authorize(credentials) {
        const ADMIN_USERNAME = process.env.NEXT_PUBLIC_ADMIN_USERNAME || 'admin';
        const ADMIN_PASSWORD_HASH = process.env.ADMIN_PASSWORD_HASH || '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9';

        if (!credentials?.username || !credentials?.password) {
          return null;
        }

        // Check username
        if (credentials.username !== ADMIN_USERNAME) {
          return null;
        }

        const passwordHash = hashPassword(credentials.password);
        if (passwordHash === ADMIN_PASSWORD_HASH) {
          return {
            id: '1',
            name: 'Admin',
            email: 'admin@example.com',
          };
        }

        return null;
      },
    }),
  ],
  pages: {
    signIn: '/login',
  },
  callbacks: {
    async jwt({ token }) {
      return token;
    },
    async session({ session }) {
      return session;
    },
  },
  secret: process.env.NEXTAUTH_SECRET || 'dev-secret-key-change-in-production',
});

export { handler as GET, handler as POST };
