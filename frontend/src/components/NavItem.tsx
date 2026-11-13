type NavItemProps = {
    label: string
    active?: boolean
}

function NavItem({ label, active = false }: NavItemProps) {
    return (
        <li className={active ? 'nav-item active' : 'nav-item'}>
            {label}
        </li>
    )
}

export default NavItem
