import '@testing-library/jest-dom';

// Mock the use client directive
jest.mock('react', () => ({
  ...jest.requireActual('react'),
  use: jest.fn((promise) => promise)
}));

// Mock next/navigation
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
    replace: jest.fn(),
    prefetch: jest.fn()
  }),
  useSearchParams: () => ({
    get: jest.fn()
  })
}));