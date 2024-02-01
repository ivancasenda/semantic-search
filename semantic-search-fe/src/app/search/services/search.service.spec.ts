import { TestBed } from '@angular/core/testing';

import { SearchService } from './search.service';
import {
  HttpClientTestingModule,
  HttpTestingController,
} from '@angular/common/http/testing';
import { Result } from 'src/app/shared/types/post';
import { HttpErrorResponse } from '@angular/common/http';
import { environment } from 'src/environments/environment.development';

/**
 * Test suite for the SearchService.
 */
describe('SearchService', () => {
  let service: SearchService;
  let httpTestingController: HttpTestingController;

  /**
   * Set up the TestBed configuration before each test.
   * Mock Http Client
   */
  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
    });
    service = TestBed.inject(SearchService);
    httpTestingController = TestBed.inject(HttpTestingController);
  });

  /**
   * Verify that there are no outstanding HTTP requests after each test.
   */
  afterEach(() => {
    httpTestingController.verify();
  });

  /**
   * Ensure that the service is created successfully.
   */
  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  /**
   * Test the fetchPosts method for handling successful retrieval of posts.
   */
  describe('fetchPosts', () => {
    // Define the base URL for the search API.
    const baseUrl = environment.apiUrl + '/search?query=';

    /**
     * Test successful retrieval of posts and handling of the response.
     */
    it('should handle retrieving posts return Observable<Post[]>', () => {
      // Define the expected result for a successful response.
      const expectedResult: Result = {
        latency: 0,
        num_matches: 1,
        matches: [
          {
            id: '1',
            distance: 0.8,
            post: {
              title: 'title1',
              body: 'body1',
              tags: ['tag1', 'tag2'],
            },
          },
        ],
      };

      // Define the search term for the test.
      const searchTerm: string = 'test';

      // Subscribe to the fetchPosts method and assert the result.
      service.fetchPosts(searchTerm).subscribe((result) => {
        expect(result.matches.length).toEqual(1);
      });

      // Expect a single HTTP request for the specified URL.
      const req = httpTestingController.expectOne(baseUrl + searchTerm);

      expect(req.request.method).toEqual('GET');

      // Flush the expected result as the response to the HTTP request.
      req.flush(expectedResult);
    });

    /**
     * Test handling of a 404 error during the fetchPosts method.
     */
    it('should handle 404 error', () => {
      const emsg = 'deliberate 404 error';
      const searchTerm = 'test';

      // Subscribe to the fetchPosts method and assert the error response.
      service.fetchPosts(searchTerm).subscribe({
        next: () => fail('should have failed with the 404 error'),
        error: (error: HttpErrorResponse) => {
          expect(error.status).withContext('status').toEqual(404);
          expect(error.error).withContext('message').toEqual(emsg);
        },
      });

      const req = httpTestingController.expectOne(baseUrl + searchTerm);

      // Respond with a mock error (404 Not Found).
      req.flush(emsg, { status: 404, statusText: 'Not Found' });
    });
  });
});
