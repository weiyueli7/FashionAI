'use client';

import { useState, use } from 'react';
import ChatInput from '@/components/stylist/ChatInput';
import Image from 'next/image';
import DataService from '@/services/DataService';

export default function ChatPage({ searchParams }) {
    const params = use(searchParams);
    const model = params.model || 'llm';

    // Component States
    const [selectedModel, setSelectedModel] = useState(model);
    const [fashionItems, setFashionItems] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [queryText, setQueryText] = useState(''); // State for query text

    // Handlers with real data
    const handleNewChat = async (message) => {
        setIsLoading(true);
        setQueryText(message.content); // Keep the query text in the state
        console.log('Content:', message.content); // Logs the user's text input
        console.log('Image:', message.image); // Logs the Base64 image or null

        try {
            // Fetch recommendations from the API
            const response = await DataService.GetFashionItems(
                message.content, // Pass user's input as queryText
                message.image // Optional image for visual query
            );
            // Sort items
            const sortedItems = {
                ...response,
                items: response.items.sort((a, b) => a.rank - b.rank),
            };
            // Log each item's image URL and rank
            sortedItems.items.forEach((item) => {
                console.log(`Image URL: ${item.image_url}, Rank: ${item.rank}`);
            });
            setFashionItems(sortedItems);
        } catch (error) {
            console.error('Error:', error);
        }
        setIsLoading(false);
    };

    const handleModelChange = (newValue) => {
        setSelectedModel(newValue);
    };

    const handleClearSearch = () => {
        setQueryText(''); // Clear the query text
        setFashionItems(null); // Clear the displayed fashion items
    };

    return (
        <div className="min-h-screen flex flex-col pt-16">
            {/* Hero Section */}
            <section className="flex-shrink-0 min-h-[400px] flex items-center justify-center bg-gradient-to-r from-[#F0E4FC] via-[#E4E6FF] to-[#EAE4FF]">
                <div className="container mx-auto px-4 max-w-3xl relative z-10 pt-20">
                    <div className="text-center">
                        <h1 className="text-4xl md:text-6xl font-bold text-gray-800 mb-6">
                            Find personalized fashion for your occasion 🌟
                        </h1>
                        <div className="bg-white/80 backdrop-blur-lg rounded-xl shadow-lg p-6">
                            <ChatInput
                                onSendMessage={handleNewChat}
                                selectedModel={selectedModel}
                                onModelChange={handleModelChange}
                            />
                        </div>
                    </div>
                </div>
            </section>

            {/* Image Display Section */}
            <div className="flex-1 container mx-auto px-4 py-12">
                {isLoading ? (
                    <div className="text-center py-12">
                        <div className="animate-pulse text-xl text-gray-600">
                            Finding perfect matches for you...
                        </div>
                    </div>
                ) : fashionItems ? (
                    <>
                        <h2 className="text-2xl font-semibold text-gray-800 mb-8">
                            Here are your outfits recommended by your AI personal stylist, Zyra:
                        </h2>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                        {fashionItems.items.map((item, index) => (
                            <div key={index} className="flex flex-col">
                                <a href={item.item_url} target="_blank" rel="noopener noreferrer">
                                    <div className="relative aspect-square rounded-xl overflow-hidden shadow-lg mb-4">
                                        <img
                                            src={item.image_url}
                                            alt={item.item_name}
                                            fill
                                            className="object-cover hover:scale-105 transition-transform duration-300"
                                        />
                                    </div>
                                </a>
                                <div className="p-4 bg-white rounded-lg shadow-sm">
                                    <h3 className="text-xl font-semibold mb-2">{item.item_name}</h3>
                                    <p className="text-sm text-gray-600 mb-2">By {item.item_brand}</p>
                                    <p className="text-gray-800">{item.item_caption}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                    </>
                ) : (
                    <div className="text-center py-12">
                        <p className="text-gray-600">
                            Describe your occasion and style preferences above to get personalized recommendations
                        </p>
                    </div>
                )}
            </div>
        </div>
    );
}


// 'use client';

// import { useState, use } from 'react';
// import ChatInput from '@/components/stylist/ChatInput';
// import Image from 'next/image';
// import DataService from '@/services/DataService';

// export default function ChatPage({ searchParams }) {
//     const params = use(searchParams);
//     const model = params.model || 'llm';

//     // Component States
//     const [selectedModel, setSelectedModel] = useState(model);
//     const [fashionItems, setFashionItems] = useState(null);
//     const [isLoading, setIsLoading] = useState(false);
//     const [queryText, setQueryText] = useState(''); // State for query text


//     // Handlers with real data
//     const handleNewChat = async (message) => {
//         setIsLoading(true);
//         setQueryText(message.content); // Keep the query text in the state
//         console.log('Content:', message.content); // Logs the user's text input
//         console.log('Image:', message.image); // Logs the Base64 image or null
    
//         try {
//             // First, send the prompt to the stylist API
//             // await DataService.postStylistPrompt(message);
//             // Fetch recommendations
//             const response = await DataService.GetFashionItems(
//                 message.content,  // Pass user's input as queryText
//                 message.image     // Optional image for visual query        
//             );
//             // Sort items
//             const sortedItems = {
//                 ...response,
//                 items: response.items.sort((a, b) => a.rank - b.rank),
//             };
//             // Log each item's image URL and rank
//             sortedItems.items.forEach((item) => {
//             console.log(`Image URL: ${item.item_url}, Rank: ${item.rank}`);
//             });
//             setFashionItems(sortedItems);
//         } catch (error) {
//             console.error('Error:', error);
//         }
//         setIsLoading(false);
//     };


//     const handleModelChange = (newValue) => {
//         setSelectedModel(newValue);
//     };

//     const handleClearSearch = () => {
//         setQueryText(''); // Clear the query text
//         setFashionItems(null); // Clear the displayed fashion items
//     };

//     return (
//         <div className="min-h-screen flex flex-col pt-16">
//             {/* Hero Section */}
//             <section className="flex-shrink-0 min-h-[400px] flex items-center justify-center bg-gradient-to-r from-[#F0E4FC] via-[#E4E6FF] to-[#EAE4FF]">
//                 <div className="container mx-auto px-4 max-w-3xl relative z-10 pt-20">
//                     <div className="text-center">
//                         <h1 className="text-4xl md:text-6xl font-bold text-gray-800 mb-6">
//                             Find personalized fashion for your occasion 🌟
//                         </h1>
//                         <div className="bg-white/80 backdrop-blur-lg rounded-xl shadow-lg p-6">
//                             <ChatInput
//                                 onSendMessage={handleNewChat}
//                                 selectedModel={selectedModel}
//                                 onModelChange={handleModelChange}
//                             />
//                         </div>
//                     </div>
//                 </div>
//             </section>

// {/* Image Display Section */}
// <div className="flex-1 container mx-auto px-4 py-12">
//                 {isLoading ? (
//                     <div className="text-center py-12">
//                         <div className="animate-pulse text-xl text-gray-600">Finding perfect matches for you...</div>
//                     </div>
//                 ) : fashionItems ? (
//                     <>
//                         <h2 className="text-2xl font-semibold text-gray-800 mb-8">
//                             Here are your outfits recommended by your AI personal stylist, Zyra:
//                         </h2>
//                         //         <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
//                 //             {fashionItems.items.map((item, index) => (
//                                 <div key={index} className="flex flex-col">
//                                     <div className="relative aspect-square rounded-xl overflow-hidden shadow-lg mb-4">
//                                         <Image 
//                                             src={item.item_url}
//                                             alt={item.item_name}
//                                             fill
//                                             className="object-cover hover:scale-105 transition-transform duration-300"
//                                         />
//                                     </div>
//                                     <div className="p-4 bg-white rounded-lg shadow-sm">
//                                         <h3 className="text-xl font-semibold mb-2">{item.item_name}</h3>
//                                         <p className="text-sm text-gray-600 mb-2">By {item.item_brand}</p>
//                                         <p className="text-gray-800">{item.item_caption}</p>
//                                     </div>
//                                 </div>
//                             ))}
//                         </div>
//                     </>
//                 ) : (
//                     <div className="text-center py-12">
//                         <p className="text-gray-600">Describe your occasion and style preferences above to get personalized recommendations</p>
//                     </div>
//                 )}
//             </div>
            
//         </div>
//     );
// // }

// </>
// ) : (
//     <div className="text-center py-12">
//         <p className="text-gray-600">Describe your occasion and style preferences above to get personalized recommendations</p>
//     </div>
// )}
// </div>

// </div>
// );
// }





// // <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
// //     {/* Group items by item_type */}
// //     {Object.entries(
// //         fashionItems.items.reduce((acc, item) => {
// //             // Group items by their type
// //             acc[item.item_type] = acc[item.item_type] || [];
// //             acc[item.item_type].push(item);
// //             return acc;
// //         }, {})
// //     ).map(([itemType, items]) => (
// //         <div key={itemType} className="mb-8">
// //             {/* Label for item_type */}
// //             <h2 className="text-2xl font-bold mb-4 capitalize">{itemType}</h2>
// //             {/* Show top items for the item_type */}
// //             {items.slice(0, 3).map((item, index) => (



// // //                 <div key={index} className="flex flex-col mb-6">
// // //                     <div className="relative aspect-square rounded-xl overflow-hidden shadow-lg mb-4">
// // //                         <Image 
// // //                             src={item.item_url}
// // //                             alt={item.item_name}
// // //                             fill
// // //                             className="object-cover hover:scale-105 transition-transform duration-300"
// // //                         />
// // //                     </div>
// // //                     <div className="p-4 bg-white rounded-lg shadow-sm">
// // //                         <h3 className="text-xl font-semibold mb-2">{item.item_name}</h3>
// // //                         <p className="text-sm text-gray-600 mb-2">By {item.item_brand}</p>
// // //                         <p className="text-gray-800">{item.item_caption}</p>
// // //                     </div>
// // //                 </div>
// // //             ))}
// // //         </div>
// // //     ))}
// // // </div>
// // // {/* 
// //                         <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
// //                             {fashionItems.items.map((item, index) => (
// //                                 <div key={index} className="flex flex-col">
// //                                     <div className="relative aspect-square rounded-xl overflow-hidden shadow-lg mb-4">
// //                                         <Image 
// //                                             src={item.image_url}
// //                                             alt={item.item_name}
// //                                             fill
// //                                             className="object-cover hover:scale-105 transition-transform duration-300"
// //                                         />
// //                                     </div>
// //                                     <div className="p-4 bg-white rounded-lg shadow-sm">
// //                                         <h3 className="text-xl font-semibold mb-2">{item.item_name}</h3>
// //                                         <p className="text-sm text-gray-600 mb-2">By {item.item_brand}</p>
// //                                         <p className="text-gray-800">{item.item_caption}</p>
// //                                     </div>
// //                                 </div>
// //                             ))}
// //                         </div>
// //  */}
