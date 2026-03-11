import { withAuth } from 'next-auth/middleware';

export default withAuth(
  function middleware(req) {
    // This function is called after authentication is verified
  },
  {
    callbacks: {
      authorized: ({ token }) => !!token,
    },
  }
);

// Specify which routes to protect
export const config = {
  matcher: ['/admin/:path*'],
};
