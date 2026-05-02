import NextAuth from 'next-auth';
export const { handlers, auth, signIn, signOut } = NextAuth({
  providers: [], // AGNT_OS: Human must configure
  session: { strategy: 'jwt', maxAge: 4 * 60 * 60 }, // 4-hour cafe laptop protection
});
