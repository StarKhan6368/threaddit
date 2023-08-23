import { useQuery } from "@tanstack/react-query";

export function HomePage() {
  const queryData = useQuery({
    queryKey: ["subthreads/all"],
    queryFn: async () => {
      return await fetch("/api/subthreads/all").then((res) => res.json());
    },
  });
  console.log(queryData);
  return <></>;
}

export default HomePage;
