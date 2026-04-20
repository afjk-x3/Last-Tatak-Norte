import re

def main():
    with open('App.tsx', 'r') as f:
        content = f.read()

    # 1. Update Navbar 'Seller Dashboard' to 'Dashboard' or 'Admin Dashboard'
    # Actually the navbar already checks role.
    # In Navbar.tsx we need to change:
    # 1. <LayoutDashboard className="w-4 h-4" /> Seller Dashboard
    # To: <LayoutDashboard className="w-4 h-4" /> {user.role === 'admin' ? 'Admin Dashboard' : 'Seller Dashboard'}
    with open('components/Navbar.tsx', 'r') as nav_f:
        nav_content = nav_f.read()
    
    # Also in Navbar.tsx:
    # { label: 'Dashboard', path: '/seller-dashboard' }
    # Let's change the Navbar so it just points to dashboard, wait App.tsx already has routes.
    # App.tsx: <Route path="/seller-dashboard" element={<Dashboard ... />} />
    # We can just change the texts in Navbar.tsx and Dashboard.tsx
    
    nav_content = nav_content.replace(
        '<LayoutDashboard className="w-4 h-4" /> Seller Dashboard',
        '<LayoutDashboard className="w-4 h-4" /> {user.role === \'admin\' ? \'Admin Dashboard\' : \'Seller Dashboard\'}'
    )
    
    nav_content = nav_content.replace(
        "displayLinks.splice(homeIndex + 1, 0, { label: 'Dashboard', path: '/seller-dashboard' });",
        "displayLinks.splice(homeIndex + 1, 0, { label: user?.role === 'admin' ? 'Admin Dashboard' : 'Seller Dashboard', path: '/seller-dashboard' });"
    )
    
    nav_content = nav_content.replace(
        "displayLinks.push({ label: 'Dashboard', path: '/seller-dashboard' });",
        "displayLinks.push({ label: user?.role === 'admin' ? 'Admin Dashboard' : 'Seller Dashboard', path: '/seller-dashboard' });"
    )
    
    with open('components/Navbar.tsx', 'w') as nav_fw:
        nav_fw.write(nav_content)

    # 2. Fix ProfilePage Admin Display
    # Go through ProfilePage variables in App.tsx
    # We need to change:
    # isSellerOrAdmin -> we also need an isAdmin variable
    # In ProfilePage:
    
    old_profile_start = """const ProfilePage: React.FC<any> = ({ user, onUpdateProfile, onNavigate }) => {
    // ... [Previous ProfilePage code remains unchanged for brevity, as we are focusing on Admin/Seller changes] ...
    // RE-INSERTING PROFILE PAGE AND OTHER COMPONENTS TO ENSURE FULL FILE INTEGRITY
    
    const { tab } = useParams();
    const navigate = useNavigate();
    const isSellerOrAdmin = user?.role === 'seller' || user?.role === 'admin';
    const [orders, setOrders] = useState<Order[]>([]);
    const activeTab = tab || (isSellerOrAdmin ? 'shop' : 'orders');"""
    
    new_profile_start = """const ProfilePage: React.FC<any> = ({ user, onUpdateProfile, onNavigate }) => {
    // ... [Previous ProfilePage code remains unchanged for brevity, as we are focusing on Admin/Seller changes] ...
    // RE-INSERTING PROFILE PAGE AND OTHER COMPONENTS TO ENSURE FULL FILE INTEGRITY
    
    const { tab } = useParams();
    const navigate = useNavigate();
    const isAdmin = user?.role === 'admin';
    const isSeller = user?.role === 'seller';
    const isSellerOrAdmin = isSeller || isAdmin;
    const [orders, setOrders] = useState<Order[]>([]);
    
    let defaultTab = 'orders';
    if (isAdmin) defaultTab = 'personal';
    else if (isSeller) defaultTab = 'shop';
    
    const activeTab = tab || defaultTab;"""
    
    content = content.replace(old_profile_start, new_profile_start)
    
    # 3. Fix ProfilePage routing in useEffect
    
    old_profile_effect = """    useEffect(() => {
        if (isSellerOrAdmin && !['shop', 'personal'].includes(activeTab)) {
            navigate('/profile/shop', { replace: true });
        } else if (!isSellerOrAdmin && !['orders', 'personal', 'addresses'].includes(activeTab)) {
            navigate('/profile/orders', { replace: true });
        }
    }, [isSellerOrAdmin, activeTab, navigate]);"""
    
    new_profile_effect = """    useEffect(() => {
        if (isAdmin && !['personal'].includes(activeTab)) {
            navigate('/profile/personal', { replace: true });
        } else if (isSeller && !['shop', 'personal'].includes(activeTab)) {
            navigate('/profile/shop', { replace: true });
        } else if (!isSellerOrAdmin && !['orders', 'personal', 'addresses'].includes(activeTab)) {
            navigate('/profile/orders', { replace: true });
        }
    }, [isAdmin, isSeller, isSellerOrAdmin, activeTab, navigate]);"""
    
    content = content.replace(old_profile_effect, new_profile_effect)
    
    # 4. Fix ProfilePage Account Menu
    
    old_menu = """                            <h3 className="text-xs font-bold text-stone-400 uppercase tracking-wider mb-4 pl-4">Account Menu</h3>
                            {isSellerOrAdmin ? (
                                <>
                                    <TabButton id="shop" label="Shop Profile" icon={<Store className="w-5 h-5" />} />
                                    <TabButton id="personal" label="Personal Information" icon={<User className="w-5 h-5" />} />
                                </>
                            ) : ("""
    
    new_menu = """                            <h3 className="text-xs font-bold text-stone-400 uppercase tracking-wider mb-4 pl-4">Account Menu</h3>
                            {isAdmin ? (
                                <>
                                    <TabButton id="personal" label="Personal Information" icon={<User className="w-5 h-5" />} />
                                </>
                            ) : isSeller ? (
                                <>
                                    <TabButton id="shop" label="Shop Profile" icon={<Store className="w-5 h-5" />} />
                                    <TabButton id="personal" label="Personal Information" icon={<User className="w-5 h-5" />} />
                                </>
                            ) : ("""
                            
    content = content.replace(old_menu, new_menu)
    
    # 5. Fix ProfilePage Shop Tab rendering
    
    old_shop_tab = "{activeTab === 'shop' && isSellerOrAdmin && ("
    new_shop_tab = "{activeTab === 'shop' && isSeller && ("
    content = content.replace(old_shop_tab, new_shop_tab)
    
    # 6. Change Dashboard Title text if Admin
    old_dash_title = """                    <div>
                        <h2 className="text-4xl font-serif font-bold text-stone-900 mb-2">Seller Dashboard</h2>
                        <p className="text-lg text-stone-500">Manage your shop, products, and incoming orders.</p>
                    </div>"""
    
    new_dash_title = """                    <div>
                        <h2 className="text-4xl font-serif font-bold text-stone-900 mb-2">{isAdmin ? 'Admin Dashboard' : 'Seller Dashboard'}</h2>
                        <p className="text-lg text-stone-500">{isAdmin ? 'Manage your platform performance and inventory.' : 'Manage your shop, products, and incoming orders.'}</p>
                    </div>"""
    
    content = content.replace(old_dash_title, new_dash_title)
    
    with open('App.tsx', 'w') as f:
        f.write(content)

main()
