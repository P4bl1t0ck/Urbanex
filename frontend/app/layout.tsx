import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import SiteNav from "@/components/SiteNav";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Urbanex",
  description: "Plataforma de gestión inmobiliaria",
};
/*The same way as Laravel, we have layouts to put or cat inside the pages, make it more fast and easy to*/
export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    
    <html lang="es" className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`} >
      <body className="min-h-full flex flex-col">
        <main className="flex-grow">
          <SiteNav />
            {children}
        </main>
      </body>
    </html>
  );
}
