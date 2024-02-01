import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { Result } from 'src/app/shared/types/post';
import { environment } from 'src/environments/environment';

/**
 * Service for handling search-related HTTP requests.
 */
@Injectable({
  providedIn: 'root',
})
export class SearchService {
  // Base API URL obtained from the environment file
  private readonly baseUrl = environment.apiUrl;

  // Define API routes for search service
  private readonly apiRoutes = {
    /**
     * Get the API route for retrieving search suggestions.
     * @returns The API route for search suggestions.
     */
    getSuggestions: () => `/search/suggestions`,

    /**
     * Get the API route for search with a specified query.
     * @param query - The search query to be included in the route.
     * @returns The API route for search with the specified query encoded to handle special characters.
     */
    searchQuery: (query: string) =>
      `/search?query=${encodeURIComponent(query)}`,
  };

  /**
   * Constructor for the SearchService.
   * @param http - Angular HttpClient service for making HTTP requests.
   */
  constructor(private http: HttpClient) {}

  /**
   * Perform an HTTP GET request to retrieve a list of search suggestions.
   * @returns Observable of search suggestions in a string array.
   */
  fetchSuggestions(): Observable<string[]> {
    return this.http.get<string[]>(
      `${this.baseUrl}${this.apiRoutes.getSuggestions()}`,
    );
  }

  /**
   * Perform an HTTP GET request for search, with the specified query.
   * @param searchTerm - The query for the search request.
   * @returns Observable of search results in the form of a Result object.
   */
  fetchPosts(searchTerm: string): Observable<Result> {
    return this.http.get<Result>(
      `${this.baseUrl}${this.apiRoutes.searchQuery(searchTerm)}`,
    );
  }
}
