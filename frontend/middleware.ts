import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

import { SESSION_COOKIE_NAME } from "@/lib/auth";

export function middleware(request: NextRequest) {
  const token = request.cookies.get(SESSION_COOKIE_NAME)?.value;
  const isAppRoute = request.nextUrl.pathname.startsWith("/app");
  const isAccessRoute =
    request.nextUrl.pathname === "/login" || request.nextUrl.pathname.startsWith("/access");

  if (isAppRoute && !token) {
    const loginUrl = new URL("/access", request.url);
    loginUrl.searchParams.set("next", request.nextUrl.pathname);
    return NextResponse.redirect(loginUrl);
  }

  if (isAccessRoute && token) {
    return NextResponse.redirect(new URL("/app", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/app/:path*", "/login", "/access/:path*"],
};
