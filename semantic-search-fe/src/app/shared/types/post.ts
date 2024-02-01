// Represents the result of a search operation.
export interface Result {
  latency: number;
  num_matches: number;
  matches: PostMatch[];
}

// Represents a match of a post in a search operation.
export interface PostMatch {
  id: string;
  distance: number;
  post: Post;
}

// Represents a post from search.
export interface Post {
  title: string;
  body: string;
  tags: string[];
}
