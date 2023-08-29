import { useMutation } from "@tanstack/react-query";
import axios from "axios";
import { useState } from "react";
import useAuthContext from "./AuthContext";
import Svg from "./Svg";
import PropTypes from "prop-types";

Vote.propTypes = {
  url: PropTypes.string,
  initialCount: PropTypes.number,
  intitalVote: PropTypes.bool,
  contentID: PropTypes.number,
  type: PropTypes.string,
};

export default function Vote({ url, intitalVote, initialCount, contentID, type }) {
  const [vote, setVote] = useState(intitalVote);
  const [voteCount, setVoteCount] = useState(initialCount);
  const { isAuthenticated } = useAuthContext();
  const { mutate } = useMutation({
    mutationFn: async ({ vote, method, contentID }) => {
      switch (method) {
        case "put":
          return axios.put(`${url}/${contentID}`, { is_upvote: vote }).then((res) => res.data);
        case "patch":
          return axios.patch(`${url}/${contentID}`, { is_upvote: vote }).then((res) => res.data);
        case "delete":
          return axios.delete(`${url}/${contentID}`).then((res) => res.data);
        default:
          break;
      }
    },
  });
  function handleVote(newVote) {
    if (!isAuthenticated) {
      return alert("You must be logged in to vote.");
    }
    if (vote === null) {
      mutate({ vote: newVote, method: "put", contentID });
      setVoteCount((voteCount) => voteCount + (newVote ? 1 : -1));
    } else if (newVote === null) {
      mutate({ vote: newVote, method: "delete", contentID });
      setVoteCount((voteCount) => voteCount - (vote ? 1 : -1));
    } else {
      mutate({ vote: newVote, method: "patch", contentID });
      setVoteCount((voteCount) => voteCount + (newVote ? 2 : -2));
    }
    setVote(newVote);
  }
  return type === "mobile" ? (
    <>
      <Svg
        type="mobileVote"
        className="w-6 h-6"
        defaultStyle={true}
        active={vote === true}
        onClick={() => handleVote(!vote ? true : null)}
      />
      <p className={vote === true ? "text-theme-red-coral" : vote === false ? "text-sky-600" : ""}>{voteCount}</p>
      <Svg
        type="mobileVote"
        className="w-6 h-6 rotate-180"
        defaultStyle={false}
        active={vote === false}
        onClick={() => handleVote(vote === false ? null : false)}
      />
    </>
  ) : (
    <>
      <div className="px-5 py-0.5 bg-orange-100 rounded-md">
        <Svg
          type="down-arrow"
          defaultStyle={true}
          className="w-10 h-10 rotate-180"
          onClick={() => handleVote(!vote ? true : null)}
          active={vote === true}
        />
      </div>
      <p className="text-lg font-semibold">
        <span className={vote === true ? "text-theme-red-coral" : vote === false ? "text-sky-600" : ""}>
          {voteCount}
        </span>
      </p>
      <div className="px-5 py-0.5 bg-blue-50 rounded-md group">
        <Svg
          type="down-arrow"
          className="w-10 h-10"
          defaultStyle={false}
          onClick={() => handleVote(vote === false ? null : false)}
          active={vote === false}
        />
      </div>
    </>
  );
}
