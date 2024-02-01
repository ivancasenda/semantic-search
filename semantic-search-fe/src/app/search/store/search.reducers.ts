import { createReducer, on } from '@ngrx/store';
import {
  searchPosts,
  searchPostsSuccess,
  searchPostsFailure,
  loadSuggestions,
  loadSuggestionsSuccess,
  loadSuggestionsFailure,
  updateSearchTerm,
  updateSearchFocus,
} from './search.actions';
import { Result } from 'src/app/shared/types/post';

/**
 * Enum representing different status types for search operations.
 */
export enum StatusTypes {
  Pending = 'pending',
  Loading = 'loading',
  Error = 'error',
  Success = 'success',
}

/**
 * Interface defining the shape of the search state.
 */
export interface SearchState {
  suggestions: string[]; // Array of search suggestions
  result: Result | null; // Result of the search operation
  error: string | null; // Error message in case of failure
  status: StatusTypes; // Current status of the search operation
  infocus: boolean; // Boolean indicating whether search input is in focus
  searchTerm: string; // Current search term
}

/**
 * Initial state for the search feature.
 */
export const initialState: SearchState = {
  suggestions: [],
  result: null,
  error: null,
  status: StatusTypes.Pending,
  infocus: false,
  searchTerm: '',
};

/**
 * Reducer function for managing search state.
 */
export const searchReducer = createReducer(
  // Supply the initial state
  initialState,

  /**
   * Update search term in the state.
   * @param state - Current state
   * @param search - New search term
   * @returns Updated state
   */
  on(updateSearchTerm, (state: SearchState, { search }) => ({
    ...state,
    searchTerm: search,
  })),

  /**
   * Toggle search focus state.
   * @param state - Current state
   * @returns Updated state
   */
  on(updateSearchFocus, (state: SearchState) => ({
    ...state,
    infocus: !state.infocus,
  })),

  /**
   * Set status to loading when loading suggestions.
   * @param state - Current state
   * @returns Updated state
   */
  on(loadSuggestions, (state: SearchState) => ({
    ...state,
    status: StatusTypes.Loading,
  })),

  /**
   * Update state when suggestions are loaded successfully.
   * @param state - Current state
   * @param suggestions - Loaded suggestions
   * @returns Updated state
   */
  on(loadSuggestionsSuccess, (state: SearchState, { suggestions }) => ({
    ...state,
    suggestions: suggestions,
    status: StatusTypes.Success,
  })),

  /**
   * Update state in case of failure to load suggestions.
   * @param state - Current state
   * @param error - Error message
   * @returns Updated state
   */
  on(loadSuggestionsFailure, (state: SearchState, { error }) => ({
    ...state,
    suggestions: [],
    error: error,
    status: StatusTypes.Error,
  })),

  /**
   * Set status to loading when searching posts.
   * @param state - Current state
   * @returns Updated state
   */
  on(searchPosts, (state: SearchState) => ({
    ...state,
    status: StatusTypes.Loading,
  })),

  /**
   * Update state when search posts operation is successful.
   * @param state - Current state
   * @param result - Search result
   * @returns Updated state
   */
  on(searchPostsSuccess, (state: SearchState, { result }) => ({
    ...state,
    result: result,
    error: null,
    status: StatusTypes.Success,
  })),

  /**
   * Update state in case of failure during search posts operation.
   * @param state - Current state
   * @param error - Error message
   * @returns Updated state
   */
  on(searchPostsFailure, (state: SearchState, { error }) => ({
    ...state,
    result: null,
    error: error,
    status: StatusTypes.Error,
  })),
);
