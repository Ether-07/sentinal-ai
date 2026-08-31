import {
    Activity,
    Bell,
    LayoutDashboard,
    Search,
    Settings,
    ShieldCheck,
} from "lucide-react";


function Sidebar({
    activePage,
    onPageChange,
}) {
    const navigationItems = [
        {
            id: "dashboard",
            label: "Dashboard",
            icon: LayoutDashboard,
        },
        {
            id: "analyze",
            label: "Analyze",
            icon: Search,
        },
        {
            id: "transactions",
            label: "Transactions",
            icon: Activity,
        },
        {
            id: "alerts",
            label: "Alerts",
            icon: Bell,
        },
    ];


    return (
        <aside className="sidebar">

            <div className="sidebar-brand">

                <div className="sidebar-brand-mark">
                    <ShieldCheck
                        size={21}
                    />
                </div>

                <div>
                    <div className="sidebar-brand-name">
                        SENTINAL AI
                    </div>

                    <div className="sidebar-brand-subtitle">
                        RISK INTELLIGENCE
                    </div>
                </div>

            </div>


            <nav className="sidebar-navigation">

                <div className="navigation-label">
                    WORKSPACE
                </div>


                {navigationItems.map(
                    (item) => {

                        const Icon =
                            item.icon;

                        return (
                            <button
                                key={
                                    item.id
                                }
                                className={
                                    `navigation-item ${
                                        activePage ===
                                        item.id
                                            ? "active"
                                            : ""
                                    }`
                                }
                                onClick={() =>
                                    onPageChange(
                                        item.id
                                    )
                                }
                            >

                                <Icon
                                    size={17}
                                />

                                <span>
                                    {
                                        item.label
                                    }
                                </span>

                            </button>
                        );
                    }
                )}

            </nav>


            <div className="sidebar-bottom">

                <button
                    className={
                        `navigation-item ${
                            activePage ===
                            "settings"
                                ? "active"
                                : ""
                        }`
                    }
                    onClick={() =>
                        onPageChange(
                            "settings"
                        )
                    }
                >

                    <Settings
                        size={17}
                    />

                    <span>
                        Settings
                    </span>

                </button>


                <div className="sidebar-system-card">

                    <div className="system-card-header">

                        <span className="system-live-dot"></span>

                        SYSTEM OPERATIONAL

                    </div>

                    <p>
                        AI risk engine is ready
                        to analyze transactions.
                    </p>

                </div>

            </div>

        </aside>
    );
}


export default Sidebar;