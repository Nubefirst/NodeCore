import NavItem from './NavItem'
import './Sidebar.css'

function Sidebar() {
    return (
        <aside className="sidebar">
            <div className="sidebar-logo">
                <h2>NodeCore</h2>
            </div>

            <nav className="sidebar-nav">
                <ul>
                    <NavItem label="Dashboard" active />
                    <NavItem label="Servers" />
                    <NavItem label="Monitoring" />
                    <NavItem label="Users" />
                    <NavItem label="Settings" />
                </ul>
            </nav>
        </aside>
    )
}

export default Sidebar
