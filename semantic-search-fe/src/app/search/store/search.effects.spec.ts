import { Observable, throwError } from 'rxjs';
import { SearchEffects } from './search.effects';
import { TestScheduler } from 'rxjs/testing';
import { Action } from '@ngrx/store';
import { TestBed } from '@angular/core/testing';
import { provideMockActions } from '@ngrx/effects/testing';
import { SearchService } from '../services/search.service';
import {
  inputSearch,
  searchPosts,
  searchPostsFailure,
  searchPostsSuccess,
} from './search.actions';
import { Result } from 'src/app/shared/types/post';
import { HttpErrorResponse } from '@angular/common/http';

/**
 * Jasmine test suite for the SearchEffects class.
 */
describe('SearchEffects', () => {
  const searchServiceSpy = jasmine.createSpyObj('searchService', [
    'fetchPosts',
  ]);

  let effects: SearchEffects;
  let actions: Observable<Action>;
  let testScheduler: TestScheduler;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        SearchEffects,
        provideMockActions(() => actions),
        { provide: SearchService, useValue: searchServiceSpy },
      ],
    });

    effects = TestBed.inject(SearchEffects);
    testScheduler = new TestScheduler((actual, expected) => {
      expect(actual).toEqual(expected);
    });
  });

  /**
   * Verifies that the SearchEffects instance is created successfully.
   */
  it('should be created', () => {
    expect(effects).toBeTruthy();
  });

  /**
   * Test suite for the return inputSearch$ Observable effect.
   */
  describe('inputSearch$', () => {
    /**
     * Verifies the behavior of the inputSearch$ effect with debouncing and filtering.
     */
    it('should dismissed first inputSearch action and return searchPosts action on second inputSearch action', () => {
      const firstSearchTerm: string = 'test1';
      const firstAction: Action = inputSearch({
        searchTerm: firstSearchTerm,
      });
      const secondSearchTerm: string = 'test2';
      const secondAction: Action = inputSearch({
        searchTerm: secondSearchTerm,
      });

      const expected: Action = searchPosts({
        searchTerm: secondSearchTerm,
      });

      testScheduler.run(({ hot, expectObservable }) => {
        actions = hot('a-b', { a: firstAction, b: secondAction });
        expectObservable(
          effects.inputSearch$({ debounce: 2, scheduler: testScheduler }),
        ).toBe('----b', { b: expected }); // a-b (2 Tick) + 2 Tick debounceTime end
      });
    });

    /**
     * Verifies the behavior of the inputSearch$ effect with multiple inputSearch actions.
     */
    it('should pass first and second inputSearch action and return both searchPosts action', () => {
      const firstSearchTerm: string = 'test1';
      const firstAction: Action = inputSearch({
        searchTerm: firstSearchTerm,
      });
      const secondSearchTerm: string = 'test2';
      const secondAction: Action = inputSearch({
        searchTerm: secondSearchTerm,
      });

      const firstExpected: Action = searchPosts({
        searchTerm: firstSearchTerm,
      });

      const secondExpected: Action = searchPosts({
        searchTerm: secondSearchTerm,
      });

      testScheduler.run(({ hot, expectObservable }) => {
        actions = hot('a--b', { a: firstAction, b: secondAction });
        expectObservable(
          effects.inputSearch$({ debounce: 2, scheduler: testScheduler }),
        ).toBe('--a--b', { a: firstExpected, b: secondExpected }); // a-- (2 Tick included debounceTime) b + 2 Tick debounceTime
      });
    });
  });

  /**
   * Test suite for the return searchPosts$ Observable effect.
   */
  describe('searchPosts$', () => {
    /**
     * Verifies the behavior of the searchPosts$ effect with a successful API response.
     */
    it('should handle searchPosts action and return searchPostsSuccess', () => {
      const responseValue: Result = {
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
      const searchTerm: string = 'test1';
      const action: Action = searchPosts({ searchTerm });
      const expected: Action = searchPostsSuccess({ result: responseValue });

      testScheduler.run(({ hot, cold, expectObservable }) => {
        actions = hot('-a', { a: action });
        const response = cold('-b|', { b: responseValue });
        searchServiceSpy.fetchPosts.and.returnValue(response);

        expectObservable(effects.searchPosts$).toBe('--b', {
          b: expected,
        });
      });
    });

    /**
     * Verifies the behavior of the searchPosts$ effect when an error occurs in the API response.
     */
    it('should handle error in searchPosts action and return searchPostsFailure', () => {
      const responseValue = new HttpErrorResponse({ error: 'Error 404' });
      const action: Action = searchPosts({ searchTerm: 'test' });
      const expected: Action = searchPostsFailure({
        error: responseValue.error,
      });

      testScheduler.run(({ hot, expectObservable }) => {
        actions = hot('-a', { a: action });
        const response = throwError(() => responseValue);

        searchServiceSpy.fetchPosts.and.returnValue(response);

        expectObservable(effects.searchPosts$).toBe('-b', {
          b: expected,
        });
      });
    });
  });
});
