import InfinitePostsLayout from "../../components/InfinitePosts";

export default function SavedPosts() {
  return (
    <div className="flex items-center p-2 w-full">
      <InfinitePostsLayout apiQueryKey="saved" linkUrl={`posts/saved`} forSaved={true} />
    </div>
  );
}
