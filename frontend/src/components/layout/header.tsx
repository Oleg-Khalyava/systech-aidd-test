/**
 * Header компонент
 * Шапка приложения с навигацией и breadcrumbs
 */

export function Header() {
    return (
        <header className="border-b bg-white">
            <div className="flex h-16 items-center px-6">
                <div className="flex items-center gap-4">
                    <h1 className="text-xl font-bold">systech-aidd Dashboard</h1>
                </div>
                <div className="ml-auto flex items-center gap-4">
                    <span className="text-sm text-gray-600">Admin Panel</span>
                </div>
            </div>
        </header>
    );
}

