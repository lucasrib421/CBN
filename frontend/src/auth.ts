import NextAuth from "next-auth"
import Keycloak from "next-auth/providers/keycloak"

const keycloakIssuer = process.env.AUTH_KEYCLOAK_ISSUER!
const internalKeycloak = process.env.KEYCLOAK_INTERNAL_URL || 'http://keycloak:8080'
const realm = 'cbn'

export const { handlers, auth, signIn, signOut } = NextAuth({
  providers: [
    Keycloak({
      clientId: process.env.AUTH_KEYCLOAK_ID!,
      clientSecret: process.env.AUTH_KEYCLOAK_SECRET!,
      issuer: keycloakIssuer,
      // Use internal URLs for server-side token exchange (Docker network)
      token: `${internalKeycloak}/realms/${realm}/protocol/openid-connect/token`,
      userinfo: `${internalKeycloak}/realms/${realm}/protocol/openid-connect/userinfo`,
    }),
  ],
  session: {
    strategy: "jwt",
  },
  callbacks: {
    authorized({ auth: session, request }) {
      const isAdminRoute = request.nextUrl.pathname.startsWith("/admin")
      if (isAdminRoute && !session) {
        return false // Redirects to signIn page
      }
      return true
    },
    async jwt({ token, account }) {
      if (account) {
        return {
          ...token,
          access_token: account.access_token,
          refresh_token: account.refresh_token,
          expires_at: account.expires_at ? account.expires_at * 1000 : undefined,
        }
      }

      // Check if token needs refresh
      if (token.expires_at && Date.now() > (token.expires_at as number)) {
        try {
          const refreshed = await refreshAccessToken(token.refresh_token as string)
          return {
            ...token,
            access_token: refreshed.access_token,
            expires_at: Date.now() + refreshed.expires_in * 1000,
            refresh_token: refreshed.refresh_token || token.refresh_token,
          }
        } catch {
          return { ...token, error: "RefreshTokenError" }
        }
      }

      return token
    },
    async session({ session, token }) {
      return {
        ...session,
        accessToken: token.access_token as string,
        error: token.error as string | undefined,
      }
    },
  },
  pages: {
    signIn: '/api/auth/signin',
  },
  trustHost: true,
})

async function refreshAccessToken(refreshToken: string) {
  const res = await fetch(
    `${internalKeycloak}/realms/${realm}/protocol/openid-connect/token`,
    {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({
        client_id: process.env.AUTH_KEYCLOAK_ID!,
        client_secret: process.env.AUTH_KEYCLOAK_SECRET!,
        grant_type: "refresh_token",
        refresh_token: refreshToken,
      }),
    }
  )
  if (!res.ok) throw new Error("Failed to refresh token")
  return res.json()
}

// Type augmentation
declare module "next-auth" {
  interface Session {
    accessToken?: string
    error?: string
  }
}

declare module "@auth/core/jwt" {
  interface JWT {
    access_token?: string
    refresh_token?: string
    expires_at?: number
    error?: string
  }
}
