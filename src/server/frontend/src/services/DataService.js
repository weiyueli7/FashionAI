import { BASE_API_URL, uuid } from "./Common";
import { mockChats } from "./SampleData";
import axios from 'axios';

console.log("BASE_API_URL:", BASE_API_URL)

// Create an axios instance with base configuration
const api = axios.create({
    baseURL: BASE_API_URL
});

const DataService = {
    Init: function () {
        // Any application initialization logic comes here
    },
    // Function to fetch fashion recommendations from API
    GetFashionItems: async function (queryText = "trending fashion items") {
        try {
            const response = await api.post('/search', {
                queryText,
                top_k: 6  // Default number of recommendations
            });
            
            return {
                description: response.data.description,
                items: response.data.items.map(item => ({
                    item_name: item.item_name,
                    item_url: item.item_url,
                    item_type: item.item_type,
                    image_url: item.image_url,
                    item_caption: item.item_caption,
                    item_brand: item.item_brand,
                    rank: item.rank,
                    score: item.score
                }))
            };
        } catch (error) {
            console.warn('Falling back to mock data:', error);
            return {
                description: "No items available.",
                items: []
            };
        }
    },

}

export default DataService;