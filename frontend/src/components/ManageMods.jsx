import { focusManager, useMutation, useQuery } from "@tanstack/react-query";
import axios from "axios";
import PropTypes from "prop-types";
import { useEffect, useState } from "react";
import Svg from "./Svg";
import Loader from "./Loader";

ManageMods.propTypes = {
  mods: PropTypes.array,
  threadId: PropTypes.number,
};

export default function ManageMods({ mods, threadId }) {
  const [modList, setModList] = useState(mods);
  const [search, setSearch] = useState("");
  const { data, isFetching } = useQuery({
    queryKey: ["search/user", search],
    queryFn: async ({ signal }) => {
      return await axios.get(`https://elegant-manifestation-production.up.railway.app/api/user/search/${search}`, { signal }).then((data) => data.data);
    },
    enabled: search.length > 3,
  });
  useEffect(() => {
    focusManager.setFocused(false);
    return () => focusManager.setFocused(true);
  }, []);
  const { mutate } = useMutation({
    mutationFn: async ({ username, isDelete = false }) => {
      if (isDelete) {
        return await axios
          .delete(`https://elegant-manifestation-production.up.railway.app/api/thread/mod/${threadId}/${username}`)
          .then((res) => {
            setModList(modList.filter((user) => user !== username));
            return res.data;
          })
          .catch((err) => {
            alert(`${err.message} - ${err.response.data.message}, Only admins can remove thread creator`);
          });
      } else {
        return await axios.put(`https://elegant-manifestation-production.up.railway.app/api/thread/mod/${threadId}/${username}`).then((res) => {
          setModList([...modList, username]);
          return res.data;
        });
      }
    },
  });
  return (
    <div className="w-5/6 h-5/6 bg-white rounded-md">
      <h1 className="pt-2 text-2xl font-semibold text-center text-theme-orange">ModList</h1>
      <ul className="overflow-auto relative p-3 m-3 space-y-2 max-h-[40vh] list-none bg-theme-cultured">
        {modList.map((mod) => (
          <li
            key={mod}
            className="flex justify-between items-center p-1 bg-white rounded-md cursor-pointer"
            onClick={() => mutate({ username: mod, isDelete: true })}>
            {mod}
            <Svg type="delete" className="w-8 h-8 font-bold text-theme-orange" />
          </li>
        ))}
      </ul>
      <div className="flex flex-col">
        <input
          type="text"
          name="username"
          id="username"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="p-2 mx-3 font-semibold border-2 md:mx-10"
          placeholder="Enter username to add new mod"
        />
        {isFetching ? (
          <div className="m-28">
            <Loader forPosts={true} />
          </div>
        ) : (
          data && (
            <ul className="overflow-auto relative p-4 m-3 space-y-2 md:max-h-[38vh] max-h-[45vh] list-none rounded-md bg-theme-cultured">
              {data?.map(
                (user) =>
                  !modList.includes(user.username) && (
                    <li
                      key={user.username}
                      className="flex justify-between items-center p-1 px-2 bg-white rounded-md cursor-pointer"
                      onClick={() => mutate({ username: user.username })}>
                      {user.username}
                      <Svg type="add" className="w-8 h-8 font-bold text-theme-orange" />
                    </li>
                  )
              )}
            </ul>
          )
        )}
      </div>
    </div>
  );
}
