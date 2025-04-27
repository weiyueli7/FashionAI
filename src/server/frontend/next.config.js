/** @type {import('next').NextConfig} */
const nextConfig = {
    reactStrictMode: true,
    webpack: (config) => {
        config.module.rules.push({
            test: /\.svg$/,
            use: ["@svgr/webpack"]
        });
        return config;
    },

    // Configure image optimization
    images: {
        domains: [
            'localhost',
            'rag-system-api-service',
            'cdn-images.farfetch-contents.com',
            // Add any other domains you'll be loading images from
        ],
        remotePatterns: [
            {
                protocol: 'https',
                hostname: '**',
                port: '',
                pathname: '**',
            },
            {
                protocol: 'http',
                hostname: 'localhost',
                port: '8000',
                pathname: '**',
            },
            {
                protocol: 'http',
                hostname: 'rag-system-api-service',
                port: '8000',
                pathname: '**',
            }
        ],
    },

    rewrites: async () => {
        return [
            {
                source: "/api/:path*",
                destination:
                    process.env.NODE_ENV === "development"
                        ? "http://rag-system-api-service:8000/:path*"
                        : "/api/",
            },
            {
                source: "/docs",
                destination:
                    process.env.NODE_ENV === "development"
                        ? "http://rag-system-api-service:8000/docs"
                        : "/api/docs",
            },
            {
                source: "/openapi.json",
                destination:
                    process.env.NODE_ENV === "development"
                        ? "http://rag-system-api-service:9000/openapi.json"
                        : "/api/openapi.json",
            },
        ];
    },
    reactStrictMode: false,
};

module.exports = nextConfig;