/**
 * MainLayout компонент
 * Основной layout без sidebar - Dashboard на весь экран
 */

import { Header } from './header';

interface MainLayoutProps {
  children: React.ReactNode;
}

export function MainLayout({ children }: MainLayoutProps) {
  return (
    <div className="flex h-screen flex-col">
      <Header />
      <main className="flex-1 overflow-y-auto bg-muted/30 p-4 md:p-6">{children}</main>
    </div>
  );
}
