import { useQuery } from "@tanstack/react-query";
import ThreadsSidebar from "../../components/ThreadsSidebar";

export function HomePage() {
  // const queryData = useQuery({
  //   queryKey: ["subthreads/all"],
  //   queryFn: async () => {
  //     return await fetch("/api/subthreads/all").then((res) => res.json());
  //   },
  // });
  // console.log(queryData);
  return (
    <>
      <ThreadsSidebar />
    </>
  );
}

export default HomePage;
