import {
    Bell,
    ChevronDown,
    Shield,
} from "lucide-react";


function Topbar() {
    return (
        <header className="topbar-dashboard">

            <div className="topbar-context">

                <div className="topbar-context-icon">
                    <Shield
                        size={17}
                    />
                </div>

                <div>
                    <div className="topbar-context-title">
                        Payment Risk Intelligence
                    </div>

                    <div className="topbar-context-subtitle">
                        AI-assisted transaction monitoring
                    </div>
                </div>

            </div>


            <div className="topbar-actions">

                <button
                    className="topbar-icon-button"
                    aria-label="Notifications"
                >
                    <Bell
                        size={17}
                    />

                    <span className="notification-dot"></span>

                </button>


                <div className="user-menu">

                    <div className="user-avatar">
                        SA
                    </div>

                    <div className="user-info">

                        <strong>
                            Security Analyst
                        </strong>

                        <span>
                            Analyst
                        </span>

                    </div>

                    <ChevronDown
                        size={15}
                    />

                </div>

            </div>

        </header>
    );
}


export default Topbar;