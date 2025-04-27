'use client';

import Link from 'next/link';

export default function Home() {
    return (
        <div className="page-wrapper">
            {/* Hero Section */}
            <section className="hero-section">
                <div className="hero-content">
                    <h1 className="hero-title">
                        Hi there! I'm Zyra, your AI Fashion Stylist
                    </h1>
                    <p className="hero-description">
                        I can help you find your perfect outfit and match accessory suggestions.
                    </p>
                    <div className="flex flex-wrap justify-center gap-4">
                        <Link href="/stylist" className="button-primary">
                            Get Started
                        </Link>
                        <Link href="/gallery" className="button-secondary">
                            Learn More
                        </Link>
                    </div>
                    {/* <div className="flex flex-wrap justify-center gap-4">
                        <button className="button-primary">Get Started</button>
                    </div> */}
                </div>
            </section>

            {/* Full-width Image Section */}
            <section className="w-full overflow-hidden">
                <div className="relative w-full h-130">
                    <img 
                        src="/assets/main-page-photo.png" 
                        alt="Fashion collection showcase"
                        className="w-full h-full object-cover"
                    />
                    {/* Optional overlay for better text contrast */}
                    <div className="absolute inset-0 bg-black bg-opacity-30"></div>
                </div>
            </section>

        </div>
    );
}