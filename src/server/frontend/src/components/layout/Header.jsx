'use client'

import { useState } from 'react'
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Home, Podcasts, Email, SmartToy, Menu, Close } from '@mui/icons-material';
import InsertChartIcon from '@mui/icons-material/InsertChart';
import LoyaltyIcon from '@mui/icons-material/Loyalty';
import ShoppingBasketIcon from '@mui/icons-material/ShoppingBasket';
import ListAltIcon from '@mui/icons-material/ListAlt';
import AppsIcon from '@mui/icons-material/Apps';

export default function Header() {
    // Component States
    const [isMenuOpen, setIsMenuOpen] = useState(false);
    const pathname = usePathname();

    const navItems = [
        { name: 'Home', path: '/', icon: <Home sx={{ fontSize: 20 }} /> },
        { name: 'Fashion Gallery', path: '/gallery', icon: <ShoppingBasketIcon fontSize="small" /> },
        { name: 'AI Stylist', path: '/stylist', icon: <LoyaltyIcon fontSize="small" /> }
    ];

    // UI View
    return (
        <>
            <header className="header-wrapper">
                <div className="header-container">
                    <div className="header-content">
                        <Link href="/" className="header-logo">
                            <span className="text-2xl">✨</span>
                            <h1 className="text-xl font-bold font-montserrat">Fashion AI</h1>
                        </Link>

                        <nav className="nav-desktop">
                            {navItems.map((item) => (
                                <Link
                                    key={item.name}
                                    href={item.path}
                                    className={`nav-link ${pathname === item.path ? 'nav-link-active' : ''}`}
                                >
                                    <div className="nav-icon-wrapper">{item.icon}</div>
                                    <span className="nav-text">{item.name}</span>
                                </Link>
                            ))}
                        </nav>

                        <button
                            className="mobile-menu-button"
                            onClick={() => setIsMenuOpen(!isMenuOpen)}
                            aria-label="Toggle menu"
                        >
                            {isMenuOpen ? <Close className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
                        </button>
                    </div>
                </div>

                <div className={`mobile-menu ${isMenuOpen ? 'translate-y-0' : '-translate-y-full'}`}>
                    {/* ... mobile menu content ... */}
                </div>
            </header>
            {isMenuOpen && <div className="mobile-menu-overlay" onClick={() => setIsMenuOpen(false)} />}
        </>
    );
}