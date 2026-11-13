import Sidebar from '../components/Sidebar'
import './MainLayout.css'
import Dashboard from '../pages/Dashboard'

function MainLayout() {
    return (
        <div className="app-layout">
            <Sidebar />

            <div className="main-area">
                <header className="header">
                    <h2>NodeCore</h2>
                </header>

                <main className="page-content">
                    <Dashboard />
                </main>
            </div>
        </div>
    )
}

export default MainLayout
