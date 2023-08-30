// Have mercy on this code
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import axios from "axios";
import PropTypes from "prop-types";
import { useEffect, useState } from "react";
import avatar from "../../assets/avatar.png";
import AuthConsumer from "../../components/AuthContext";
import Svg from "../../components/Svg";
import { useRef } from "react";

export function Inbox() {
  const [curChat, setCurChat] = useState(false);
  const { data, isFetching } = useQuery({
    queryKey: ["inbox"],
    queryFn: async () => {
      return await axios.get("/api/messages/inbox").then((res) => res.data);
    },
  });
  if (isFetching) {
    return <></>;
  }
  return (
    <div className="flex flex-1">
      {!curChat && (
        <ul className="md:hidden p-4 m-2.5 space-y-2 list-none bg-white rounded-md w-full">
          <div className="flex justify-between items-center py-3 border-b-2">
            <h1 className="text-2xl font-semibold text-blue-600">Messages</h1>
          </div>
          {data?.map((message) => (
            <li
              className={`w-full flex items-center p-3 space-x-2 rounded-xl cursor-pointer ${
                curChat.name === message.sender.name ? "bg-blue-200" : "hover:bg-blue-200"
              }`}
              key={message.message_id}
              onClick={() => setCurChat(message.sender)}>
              <img src={message.sender.avatar || avatar} className="w-14 h-14 rounded-full" alt="" />
              <div className="flex flex-col space-y-1 w-full">
                <div className="flex justify-between items-center w-full ">
                  <p className="font-medium">{message.sender.name}</p>
                  {!message.latest_from_user && !message.seen && (
                    <Svg type="mail" className="w-4 h-4 text-theme-orange" />
                  )}
                </div>
                <p className="text-sm">
                  {message.latest_from_user ? "You: " : `${message.receiver.name}: `}
                  {message.content.slice(0, 15)}
                  {message.content.length > 15 ? "..." : ""}
                </p>
              </div>
            </li>
          ))}
        </ul>
      )}
      <ul className="hidden md:block p-4 m-2.5 space-y-2 list-none bg-white rounded-md">
        <div className="flex justify-between items-center py-3 border-b-2">
          <h1 className="text-2xl font-semibold text-blue-600">Messages</h1>
        </div>
        {data?.map((message) => (
          <li
            className={`flex items-center w-full p-3 space-x-2 rounded-xl cursor-pointer ${
              curChat.name === message.sender.name ? "bg-blue-200" : "hover:bg-blue-200"
            }`}
            key={message.message_id}
            onClick={() => setCurChat(message.sender)}>
            <img src={message.sender.avatar || avatar} className="w-14 h-14 rounded-full" alt="" />
            <div className="flex flex-col space-y-1 w-full">
              <div className="flex justify-between items-center w-full ">
                <p className="font-medium">{message.receiver.name}</p>
                {!message.latest_from_user && !message.seen && (
                  <Svg type="mail" className="w-4 h-4 text-theme-orange" />
                )}
              </div>
              <p className="text-sm">
                {message.latest_from_user ? "You: " : `${message.receiver.name}: `}
                {message.content.slice(0, 15)}
                {message.content.length > 15 ? "..." : ""}
              </p>
            </div>
          </li>
        ))}
      </ul>
      {curChat && (
        <div className={`flex-1 m-2.5 bg-white rounded-md ${!curChat && "flex justify-center items-center"}`}>
          <Chat sender={curChat} setCurChat={setCurChat} />
        </div>
      )}
    </div>
  );
}

Chat.propTypes = {
  sender: PropTypes.shape({
    avatar: PropTypes.string,
    name: PropTypes.string,
  }),
  setCurChat: PropTypes.func,
};
function Chat({ sender, setCurChat }) {
  const myRef = useRef(null);
  const queryClient = useQueryClient();
  const { user } = AuthConsumer();
  const [message, setMessage] = useState("");
  const { data, isFetching } = useQuery({
    queryKey: ["chat", sender.name],
    queryFn: async () => {
      return await axios.get(`/api/messages/all/${sender.name}`).then((res) => res.data);
    },
    enabled: sender.name !== undefined,
  });
  const { mutate } = useMutation({
    mutationFn: async (params) => {
      return await axios
        .post("/api/messages", { content: params.message, receiver: params.sender.name })
        .then((res) => res.data);
    },
    onSuccess: () => {
      setMessage("");
      queryClient.invalidateQueries({ queryKey: ["chat", sender.name] });
    },
  });
  useEffect(() => {
    myRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [isFetching]);
  if (isFetching) {
    return <></>;
  }
  return (
    <div className="flex flex-col justify-between w-full">
      <div className="flex items-center p-3 mx-2 border-b-2 justify-between">
        <div className="flex space-x-4 items-center">
          <img src={sender.avatar || avatar} alt="" className="w-14 h-14 rounded-full" />
          <p className="text-xl font-semibold">{sender.name}</p>
        </div>
        <button
          onClick={() => setCurChat(false)}
          className="ml-auto justify-self-end p-2 rounded-md text-white bg-blue-600">
          Close
        </button>
      </div>
      <ul className="p-3 space-y-3 rounded-md md:h-[63vh] h-[70vh] overflow-auto">
        {data?.map((message) => (
          <Message message={message} toUser={message.sender.name == user.username} key={message.message_id} />
        ))}
        <li className="invisible" key={"scrollToElement"} ref={myRef}></li>
      </ul>
      <form
        onSubmit={(e) => {
          e.preventDefault();
          mutate({ message, sender });
        }}
        className="p-4 bg-blue-200 w-full flex justify-between items-center ">
        <input
          type="text"
          className="font-medium p-2 px-4 focus:outline-none mx-3 w-full rounded-full"
          placeholder="Type a message"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
        />
        <Svg onClick={() => mutate({ message, sender })} type="send" className="w-8 h-8 bg-inherit text-white" />
      </form>
    </div>
  );
}

Message.propTypes = {
  message: PropTypes.object,
  toUser: PropTypes.bool,
};
function Message({ message, toUser }) {
  const sentDate = new Date(message.created_at);
  return (
    <li
      className={` pl-2 py-1 w-fit rounded-md ${message.seen ? "bg-green-100" : "bg-blue-100"} ${
        toUser ? "ml-auto pr-2" : "pr-10"
      }`}>
      <p className={`break-all pt-1 font-medium ${toUser && "pl-1"}`}>{message.content}</p>
      <p className={`mt-0.5 text-xs font-light ${toUser && "text-right"}`}>{sentDate.toLocaleString()}</p>
    </li>
  );
}

export default Inbox;
