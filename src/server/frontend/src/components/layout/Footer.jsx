'use client'
import { usePathname } from 'next/navigation';

export default function Footer() {
    // Component States
    const pathname = usePathname();
    if (pathname === '/chat') return null;

    // UI View
    return (
        <footer className="footer">
            <div className="layout-container">
                <p className="footer-text">
                    Copyright © {new Date().getFullYear()} Fashion AI 2024 - All Rights Reserved.
                </p>
            </div>
        </footer>
    );
}