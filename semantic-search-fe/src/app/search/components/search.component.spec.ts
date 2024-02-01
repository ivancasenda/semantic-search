import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideMockStore, MockStore } from '@ngrx/store/testing';

import { SearchComponent } from './search.component';
import { DarkmodeComponent } from 'src/app/darkmode/components/darkmode/darkmode.component';
import { AppState } from 'src/app/app.state';
import { inputSearch } from '../store/search.actions';
import {
  selectLoadingStatus,
  selectSearchResult,
} from '../store/search.selectors';
import { By } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';

/**
 * Test suite for the SearchComponent.
 */
describe('SearchComponent', () => {
  // Declare variables for the component, fixture, and NgRx store.
  let component: SearchComponent;
  let fixture: ComponentFixture<SearchComponent>;
  let store: MockStore<AppState>;

  // Define mock selectors for NgRx store.
  const mockSelectors = {
    selectors: [
      {
        selector: selectSearchResult,
        value: {
          latency: 0,
          num_matches: 2,
          matches: [
            // Mock search result data
            {
              id: '1',
              distance: 0.8,
              post: {
                title: 'title1',
                body: 'body1',
                tags: ['tag1', 'tag2'],
              },
            },
            {
              id: '2',
              distance: 0.7,
              post: {
                title: 'title2',
                body: 'body2',
                tags: ['tag1', 'tag2'],
              },
            },
          ],
        },
      },
      {
        selector: selectLoadingStatus,
        value: true,
      },
    ],
  };

  /**
   * Set up the TestBed configuration before each test.
   * Provide Mock NgRx Store and Spy on NgRx Dispatch.
   */
  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [SearchComponent, DarkmodeComponent],
      providers: [provideMockStore(mockSelectors)],
      imports: [BrowserAnimationsModule],
    });

    fixture = TestBed.createComponent(SearchComponent);
    component = fixture.componentInstance;

    store = TestBed.inject(MockStore);

    fixture.detectChanges();

    spyOn(store, 'dispatch').and.callFake(() => {});
  });

  /**
   * Ensure that the component is created successfully.
   */
  it('should create', () => {
    expect(component).toBeTruthy();
  });

  /**
   * Test the inputSearch method to ensure it dispatches the inputSearch action.
   */
  describe('dispatcher', () => {
    it('should dispatch inputSearch action', () => {
      const searchTerm = 'test';
      component.inputSearch(searchTerm);
      expect(store.dispatch).toHaveBeenCalledWith(inputSearch({ searchTerm }));
    });
  });

  /**
   * Test selectors for rendering posts (search result) and loading state.
   */
  describe('selectors', () => {
    /**
     * Test rendering of posts in the search result.
     */
    describe('show posts', () => {
      it('should render all posts search result', () => {
        expect(fixture.debugElement.queryAll(By.css('#post')).length).toEqual(
          2,
        );
      });
    });

    /**
     * Test rendering of loading state.
     */
    describe('is loading', () => {
      it('should render loading state', () => {
        expect(
          fixture.debugElement.queryAll(By.css('#loading')).length,
        ).toEqual(1);
      });

      it('should not render loading state', () => {
        // Override loading status to false for the second test case.
        store.overrideSelector(selectLoadingStatus, false);
        store.refreshState();
        fixture.detectChanges();

        expect(
          fixture.debugElement.queryAll(By.css('#loading')).length,
        ).toEqual(0);
      });
    });
  });
});
