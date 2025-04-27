import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ChatPage from './page';

// Mock the DataService module
jest.mock('../../../services/DataService', () => ({
  GetFashionItems: jest.fn(),
}));

// Mock the ChatInput component
jest.mock('../../../components/stylist/ChatInput', () => {
  return function MockChatInput({ onSendMessage, selectedModel, onModelChange }) {
    return (
      <div data-testid="mock-chat-input">
        <input
          type="text"
          data-testid="chat-input"
          onChange={(e) => {}}
          onKeyPress={(e) => {
            if (e.key === 'Enter') {
              onSendMessage({ content: e.target.value, image: null });
            }
          }}
        />
        <select
          data-testid="model-select"
          value={selectedModel}
          onChange={(e) => onModelChange(e.target.value)}
        >
          <option value="llm">LLM</option>
          <option value="other">Other</option>
        </select>
      </div>
    );
  };
});

// Mock next/image
jest.mock('next/image', () => ({
  __esModule: true,
  default: (props) => {
    // eslint-disable-next-line @next/next/no-img-element
    return <img {...props} src={props.src || ''} alt={props.alt || ''} />
  },
}));

// Import the mocked DataService
const DataService = require('../../../services/DataService');

// Mock sample fashion items
const mockFashionItems = {
  items: [
    {
      item_type: "dress",
      item_url: "https://example.com/dress1.jpg",
      item_name: "Summer Dress",
      item_brand: "Brand A",
      item_caption: "Beautiful summer dress",
      rank: 1
    },
    {
      item_type: "shoes",
      item_url: "https://example.com/shoes1.jpg",
      item_name: "Casual Sneakers",
      item_brand: "Brand B",
      item_caption: "Comfortable sneakers",
      rank: 2
    }
  ]
};

describe('ChatPage', () => {
  beforeEach(() => {
    // Clear all mocks before each test
    jest.clearAllMocks();
  });

  it('renders the initial state correctly', () => {
    render(<ChatPage searchParams={{}} />);
    
    // Check if the hero section is rendered
    expect(screen.getByText(/Find personalized fashion for your occasion/i)).toBeInTheDocument();
    
    // Check if the initial empty state message is shown
    expect(screen.getByText(/Describe your occasion and style preferences above to get personalized recommendations/i)).toBeInTheDocument();
    
    // Check if ChatInput is rendered
    expect(screen.getByTestId('mock-chat-input')).toBeInTheDocument();
  });

  it('handles model change correctly', async () => {
    render(<ChatPage searchParams={{}} />);
    
    const modelSelect = screen.getByTestId('model-select');
    fireEvent.change(modelSelect, { target: { value: 'other' } });
    
    expect(modelSelect.value).toBe('other');
  });

  it('handles new chat message and displays fashion items', async () => {
    // Mock the API response
    DataService.GetFashionItems.mockResolvedValueOnce(mockFashionItems);
    
    render(<ChatPage searchParams={{}} />);
    
    // Simulate sending a message
    const chatInput = screen.getByTestId('chat-input');
    fireEvent.change(chatInput, { target: { value: 'summer outfit' } });
    fireEvent.keyPress(chatInput, { key: 'Enter', code: 13, charCode: 13 });
    
    // Check loading state
    expect(screen.getByText(/Finding perfect matches for you.../i)).toBeInTheDocument();
    
    // Wait for the results to be displayed
    await waitFor(() => {
      expect(screen.getByText(/Here are your outfits recommended by your AI personal stylist, Zyra:/i)).toBeInTheDocument();
    });
    
    // Verify that the fashion items are displayed
    expect(screen.getByText('Summer Dress')).toBeInTheDocument();
    expect(screen.getByText('Casual Sneakers')).toBeInTheDocument();
    
    // Verify that the API was called with correct parameters
    expect(DataService.GetFashionItems).toHaveBeenCalledWith('summer outfit', null);
  });

  it('handles API errors gracefully', async () => {
    // Mock API error
    DataService.GetFashionItems.mockRejectedValueOnce(new Error('API Error'));
    
    // Spy on console.error
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
    
    render(<ChatPage searchParams={{}} />);
    
    // Simulate sending a message
    const chatInput = screen.getByTestId('chat-input');
    fireEvent.change(chatInput, { target: { value: 'summer outfit' } });
    fireEvent.keyPress(chatInput, { key: 'Enter', code: 13, charCode: 13 });
    
    // Verify error was logged
    await waitFor(() => {
      expect(consoleSpy).toHaveBeenCalled();
    });
    
    // Clean up
    consoleSpy.mockRestore();
  });

  it('groups fashion items by item_type correctly', async () => {
    // Mock API response with multiple items of the same type
    const mockGroupedItems = {
      items: [
        {
          item_type: "dress",
          item_url: "https://example.com/dress1.jpg",
          item_name: "Summer Dress 1",
          item_brand: "Brand A",
          item_caption: "Beautiful summer dress",
          rank: 1
        },
        {
          item_type: "dress",
          item_url: "https://example.com/dress2.jpg",
          item_name: "Summer Dress 2",
          item_brand: "Brand B",
          item_caption: "Another beautiful dress",
          rank: 2
        }
      ]
    };
    
    DataService.GetFashionItems.mockResolvedValueOnce(mockGroupedItems);
    
    render(<ChatPage searchParams={{}} />);
    
    // Simulate sending a message
    const chatInput = screen.getByTestId('chat-input');
    fireEvent.change(chatInput, { target: { value: 'dresses' } });
    fireEvent.keyPress(chatInput, { key: 'Enter', code: 13, charCode: 13 });
    
    await waitFor(() => {
      // Check if items are grouped under the "dress" category
      expect(screen.getByText('dress')).toBeInTheDocument();
      expect(screen.getByText('Summer Dress 1')).toBeInTheDocument();
      expect(screen.getByText('Summer Dress 2')).toBeInTheDocument();
    });
  });

  it('maintains loading state during API calls', async () => {
    // Mock API with delay
    DataService.GetFashionItems.mockImplementation(
      () => new Promise(resolve => setTimeout(() => resolve(mockFashionItems), 100))
    );
    
    render(<ChatPage searchParams={{}} />);
    
    // Simulate sending a message
    const chatInput = screen.getByTestId('chat-input');
    fireEvent.change(chatInput, { target: { value: 'summer outfit' } });
    fireEvent.keyPress(chatInput, { key: 'Enter', code: 13, charCode: 13 });
    
    // Verify loading state is shown
    expect(screen.getByText(/Finding perfect matches for you.../i)).toBeInTheDocument();
    
    // Wait for loading to complete
    await waitFor(() => {
      expect(screen.queryByText(/Finding perfect matches for you.../i)).not.toBeInTheDocument();
    });
  });

  it('handles empty search params correctly', () => {
    render(<ChatPage searchParams={{}} />);
    const modelSelect = screen.getByTestId('model-select');
    expect(modelSelect.value).toBe('llm'); // Should default to 'llm'
  });

  it('handles search params with model specified', () => {
    render(<ChatPage searchParams={{ model: 'other' }} />);
    const modelSelect = screen.getByTestId('model-select');
    expect(modelSelect.value).toBe('other');
  });
});

// import React from 'react';
// import { render, screen, fireEvent, waitFor } from '@testing-library/react';
// import '@testing-library/jest-dom'; // Provides useful matchers
// import page from './page';
// import DataService from '@services/DataService';

// // Mock the DataService API
// jest.mock('@services/DataService', () => ({
//     GetFashionItems: jest.fn(),
// }));

// describe('ChatPage Component', () => {
//     const mockFashionItems = {
//         items: [
//             { item_name: "T-Shirt", item_caption: "Casual wear", item_url: "/images/tshirt.jpg", item_brand: "Brand A", item_type: "Clothing", rank: 1 },
//             { item_name: "Jeans", item_caption: "Blue denim", item_url: "/images/jeans.jpg", item_brand: "Brand B", item_type: "Clothing", rank: 2 },
//             { item_name: "Sneakers", item_caption: "Comfortable footwear", item_url: "/images/sneakers.jpg", item_brand: "Brand C", item_type: "Shoes", rank: 1 },
//         ],
//     };

//     beforeEach(() => {
//         // Mock the API to resolve with the mock fashion items
//         DataService.GetFashionItems.mockResolvedValue(mockFashionItems);
//     });

//     afterEach(() => {
//         jest.clearAllMocks(); // Reset mocks between tests
//     });

//     it('renders the initial UI correctly', () => {
//         render(<ChatPage searchParams={{ model: 'llm' }} />);

//         // Check that the hero section is present
//         expect(screen.getByText('Find personalized fashion for your occasion 🌟')).toBeInTheDocument();

//         // Check that the placeholder for recommendations is displayed
//         expect(
//             screen.getByText('Describe your occasion and style preferences above to get personalized recommendations')
//         ).toBeInTheDocument();
//     });

//     it('handles user input and displays loading state', async () => {
//         render(<ChatPage searchParams={{ model: 'llm' }} />);

//         // Simulate user entering a message in the ChatInput
//         const inputField = screen.getByPlaceholderText('What are you looking for today?');
//         fireEvent.change(inputField, { target: { value: 'Summer outfits' } });

//         // Simulate submitting the message
//         const sendButton = screen.getByRole('button', { name: /send/i });
//         fireEvent.click(sendButton);

//         // Check loading state
//         expect(screen.getByText('Finding perfect matches for you...')).toBeInTheDocument();

//         // Wait for API to resolve and items to render
//         await waitFor(() => {
//             expect(DataService.GetFashionItems).toHaveBeenCalledWith('Summer outfits', null);
//         });

//         // Check that the items are grouped and displayed
//         expect(screen.getByText('Clothing')).toBeInTheDocument();
//         expect(screen.getByText('Shoes')).toBeInTheDocument();
//         expect(screen.getByText('T-Shirt')).toBeInTheDocument();
//         expect(screen.getByText('Sneakers')).toBeInTheDocument();
//     });

//     it('clears the search and results when handleClearSearch is called', async () => {
//         render(<ChatPage searchParams={{ model: 'llm' }} />);

//         // Simulate user entering a message and fetching items
//         const inputField = screen.getByPlaceholderText('What are you looking for today?');
//         fireEvent.change(inputField, { target: { value: 'Summer outfits' } });
//         const sendButton = screen.getByRole('button', { name: /send/i });
//         fireEvent.click(sendButton);

//         // Wait for items to render
//         await waitFor(() => {
//             expect(screen.getByText('Clothing')).toBeInTheDocument();
//         });

//         // Simulate clearing the search
//         const clearButton = screen.getByRole('button', { name: /clear/i });
//         fireEvent.click(clearButton);

//         // Check that the input field and results are cleared
//         expect(inputField.value).toBe('');
//         expect(screen.getByText('Describe your occasion and style preferences above to get personalized recommendations')).toBeInTheDocument();
//     });
// });
