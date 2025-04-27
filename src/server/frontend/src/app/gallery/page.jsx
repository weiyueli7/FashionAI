'use client'

import Image from 'next/image';
import { useState, useEffect } from 'react';
import DataService from '@/services/DataService';

export default function StyleTransferPage() {
    const [fashionStyles, setFashionStyles] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [queryText, setQueryText] = useState({});
    const [selectedModel, setSelectedModel] = useState('llm');

    // Style categories definition with initial empty images array
    const styleCategories = [
        {
            style: "Casual Chic",
            description: "Effortlessly stylish everyday wear combining comfort and fashion",
            queryText: "casual chic everyday comfortable stylish fashion items",
            images: [] // Initialize empty images array
        },
        {
            style: "Business Professional",
            description: "Sophisticated and polished looks for the modern workplace",
            queryText: "business professional formal office work attire fashion",
            images: []
        },
        {
            style: "Bohemian",
            description: "Free-spirited and artistic styles with flowing silhouettes",
            queryText: "bohemian boho artistic flowing relaxed fashion style",
            images: []
        },
        {
            style: "Streetwear",
            description: "Urban-inspired contemporary fashion with bold elements",
            queryText: "streetwear urban contemporary bold modern fashion",
            images: []
        },
        {
            style: "Minimalist",
            description: "Clean lines and simple silhouettes in neutral tones",
            queryText: "minimalist clean simple neutral classic fashion items",
            images: []
        },
        {
            style: "Glamorous Evening",
            description: "Elegant and sophisticated looks for special occasions",
            queryText: "glamorous evening formal elegant sophisticated fashion",
            images: []
        }
    ];


    // Handle new chat with query propagation to all styles
    const handleNewChat = async (message) => {
        setIsLoading(true);
        setQueryText(message.content);
        console.log('Content:', message.content);
        console.log('Image:', message.image);

        try {
            // Fetch recommendations for each style
            const allStyleResults = await Promise.all(
                styleCategories.map(async (category) => {
                    const response = await DataService.GetFashionItems(
                        category.queryText,
                        message.image
                    );
                    return {
                        ...category,
                        items: response.items.sort((a, b) => a.rank - b.rank)
                    };
                })
            );

            // Log results for each style
            allStyleResults.forEach((styleResult) => {
                console.log(`Style: ${styleResult.style}`);
                styleResult.items.forEach((item) => {
                    console.log(`Image URL: ${item.image_url}, Rank: ${item.rank}`);
                });
            });

            setFashionStyles(allStyleResults);
        } catch (error) {
            console.error('Error:', error);
        }
        setIsLoading(false);
    };

    // Initial fetch
    useEffect(() => {
        // Trigger initial fetch with default query
        handleNewChat({ 
            content: "Show me fashion items", 
            image: null 
        });
    }, []);



    return (
        <div className="min-h-screen pt-20 pb-12 px-4">
        <div className="container mx-auto max-w-7xl">
            {/* Header */}
            <div className="mb-12">
                <h1 className="text-3xl md:text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-600 via-pink-500 to-orange-400 font-montserrat">
                    Fashion Style Gallery
                </h1>
                <p className="text-gray-600 mt-2">
                    Explore our curated collection of fashion styles
                </p>
            </div>
    
            {/* Loading State */}
            {isLoading ? (
                <div className="text-center py-20">
                    <div className="animate-pulse text-xl text-gray-600">
                        Loading fashion styles...
                    </div>
                </div>
            ) : (
                /* Style Galleries */
                <div className="space-y-16">
                    {fashionStyles.map((gallery, index) => (
                        <div key={index} className="bg-white rounded-xl shadow-sm p-8">
                            {/* Style Section Header */}
                            <div className="mb-6">
                                <h2 className="text-2xl font-semibold text-gray-800">
                                    {gallery.style}
                                </h2>
                                <p className="text-gray-600 mt-1">
                                    {gallery.description}
                                </p>
                            </div>
    
                            {/* Images Grid */}
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                                {gallery.items && gallery.items.map((item, itemIndex) => (
                                    <div key={itemIndex} className="flex flex-col">
                                        <a 
                                            href={item.item_url} 
                                            target="_blank" 
                                            rel="noopener noreferrer"
                                        >
                                            <div className="relative aspect-square rounded-xl overflow-hidden shadow-lg mb-4">
                                                <img 
                                                    src={item.image_url}
                                                    alt={item.item_name}
                                                    fill
                                                    className="object-cover hover:scale-105 transition-transform duration-300"
                                                />
                                                <div className="absolute top-2 left-2 bg-black bg-opacity-70 text-white px-2 py-1 rounded-full text-sm">
                                                    {/* Rank #{item.rank} */}
                                                </div>
                                            </div>
                                        </a>
                                        <div className="p-4 bg-gray-50 rounded-lg">
                                            <div className="flex justify-between items-start mb-2">
                                                <h3 className="text-lg font-semibold">{item.item_name}</h3>
                                                <span className="text-purple-600 font-semibold">
                                                    {/* ${Math.floor(Math.random() * 150) + 50} */}
                                                </span>
                                            </div>
                                            <p className="text-sm text-gray-600 mb-2">By {item.item_brand}</p>
                                            <p className="text-gray-800 text-sm">{item.item_caption}</p>
                                            <div className="mt-2 text-sm text-gray-500">
                                                {/* Match Score: {Math.round(item.score * 100)}% */}
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    </div>    
    );
}
