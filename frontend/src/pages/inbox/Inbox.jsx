// Have mercy on this code
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import axios from "axios";
import { AnimatePresence, motion } from "framer-motion";
import PropTypes from "prop-types";
import { useEffect, useRef, useState } from "react";
import avatar from "../../assets/avatar.png";
import AuthConsumer from "../../components/AuthContext";
import Svg from "../../components/Svg";
import Loader from "../../components/Loader";
import { Link } from "react-router-dom";

export function Inbox() {
  const [curChat, setCurChat] = useState(false);
  const { data } = useQuery({
    queryKey: ["inbox"],
    queryFn: async () => {
      return await axios.get("https://threaddit.onrender.com/api/messages/inbox").then((res) => res.data);
    },
  });
  useEffect(() => {
    if (curChat) {
      document.title = `Inbox | ${curChat.username}`;
    }
    else {
      document.title = "Threaddit | Inbox";
    }
    return () => {
      document.title = "Threaddit";
    };
  })
  return (
    <div className="flex flex-1">
      {!curChat && (
        <ul className="md:hidden p-4 m-2.5 space-y-2 list-none bg-white rounded-md w-full">
          <div className="flex justify-between items-center py-3 border-b-2">
            <h1 className="text-2xl font-semibold text-blue-600">Messages</h1>
          </div>
          {data?.map((message) => (
            <li
              className={`w-full flex items-center p-3 space-x-2 rounded-xl cursor-pointer ${curChat.username === message.sender.username ? "bg-blue-200" : "hover:bg-blue-200"
                }`}
              key={message.message_id}
              onClick={() => setCurChat(message.sender)}>
              <img src={message.sender.avatar || avatar} className="object-cover w-14 h-14 rounded-full" alt="" />
              <div className="flex flex-col space-y-1 w-full">
                <div className="flex justify-between items-center w-full">
                  <p className="font-medium">{message.sender.username}</p>
                  {!message.latest_from_user && !message.seen && (
                    <Svg type="mail" className="w-4 h-4 text-theme-orange" />
                  )}
                </div>
                <p className="text-sm">
                  {message.latest_from_user ? "You: " : `${message.receiver.username}: `}
                  {message.content.slice(0, 15)}
                  {message.content.length > 15 ? "..." : ""}
                </p>
              </div>
            </li>
          ))}
        </ul>
      )}
      <ul className="hidden md:block p-4 w-1/5 m-2.5 space-y-2 list-none bg-white rounded-md">
        <div className="flex justify-between items-center py-3 border-b-2">
          <h1 className="text-2xl font-semibold text-blue-600">Messages</h1>
        </div>
        {data?.map((message, index) => (
          <motion.li
            initial={{ opacity: 0, x: -100 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.25, delay: index * 0.25 }}
            className={`flex items-center w-full p-3 space-x-2 rounded-xl cursor-pointer ${curChat.username === message.sender.username ? "bg-blue-200" : "hover:bg-blue-200"
              }`}
            key={message.message_id}
            onClick={() => setCurChat(message.sender)}>
            <img src={message.sender.avatar || avatar} className="object-cover w-14 h-14 rounded-full" alt="" />
            <div className="flex flex-col space-y-1 w-full">
              <div className="flex justify-between items-center w-full">
                <p className="font-medium">{message.sender.username}</p>
                {!message.latest_from_user && !message.seen && (
                  <Svg type="mail" className="w-4 h-4 text-theme-orange" />
                )}
              </div>
              <p className="text-sm">
                {message.latest_from_user ? "You: " : `${message.receiver.username}: `}
                {message.content.slice(0, 15)}
                {message.content.length > 15 ? "..." : ""}
              </p>
            </div>
          </motion.li>
        ))}
      </ul>
      <AnimatePresence>
        {curChat && (
          <div className={`flex-1 m-2.5 bg-white rounded-md ${!curChat && "flex justify-center items-center"}`}>
            <Chat sender={curChat} setCurChat={setCurChat} />
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}

Chat.propTypes = {
  sender: PropTypes.shape({
    avatar: PropTypes.string,
    name: PropTypes.string,
    username: PropTypes.string,
  }),
  setCurChat: PropTypes.func,
  newChat: PropTypes.bool,
};
export function Chat({ sender, setCurChat, newChat = false }) {
  const myRef = useRef(null);
  const queryClient = useQueryClient();
  const { user } = AuthConsumer();
  const [message, setMessage] = useState("");
  const { data, isFetching } = useQuery({
    queryKey: ["chat", sender.username],
    queryFn: async () => {
      return await axios.get(`https://threaddit.onrender.com/api/messages/all/${sender.username}`).then((res) => res.data);
    },
    enabled: sender.username !== undefined,
  });
  const { mutate } = useMutation({
    mutationFn: async (params) => {
      return await axios
        .post("https://threaddit.onrender.com/api/messages", { content: params.message, receiver: params.sender.username })
        .then((res) => res.data);
    },
    onSuccess: (data) => {
      setMessage("");
      queryClient.setQueryData({ queryKey: ["chat", sender.username] }, (oldData) => {
        return [...oldData, data];
      });
      queryClient.setQueryData({ queryKey: ["inbox"] }, (oldData) => {
        return oldData.map((m) =>
          m.sender == sender
            ? { ...m, content: data.content, created_at: data.created_a, message_id: data.message_id }
            : m
        );
      });
    },
  });
  useEffect(() => {
    myRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [isFetching]);
  const animateWhen = data?.length - 10;
  const AnimateChat = {
    hidden: {
      opacity: 0,
      x: 10,
    },
    visible: {
      opacity: 1,
      x: 0,
    },
  };
  return (
    <motion.div
      className={`flex flex-col justify-between w-full ${newChat && "bg-white w-10/12 md:w-1/2"}`}
      variants={AnimateChat}
      initial="hidden"
      animate="visible"
      transition={{ duration: 0.25 }}
      exit={{ opacity: 0, x: 10, transition: { duration: 0.1 } }}>
      <div className="flex justify-between items-center p-3 mx-2 border-b-2">
        <div className="flex items-center space-x-4">
          <img src={sender.avatar || avatar} alt="" className="object-cover w-14 h-14 rounded-full" />
          <Link to={`/u/${sender.username}`} className="text-xl font-semibold text-blue-500">
            {sender.username}
          </Link>
        </div>
        <button
          onClick={() => setCurChat(false)}
          className="justify-self-end p-2 ml-auto text-white bg-blue-600 rounded-md">
          Close
        </button>
      </div>
      {isFetching ? (
        <div className={`${newChat ? "h-[20vh]" : "md:h-[61vh] h-[70vh]"} flex justify-center items-center`}>
          <Loader forPosts={true} />
        </div>
      ) : (
        <ul className="p-3 space-y-3 rounded-md overflow-auto md:h-[61vh] h-[70vh]">
          {data?.map((message, index) => (
            <Message
              message={message}
              messageIndex={index < animateWhen ? 0 : index - animateWhen}
              toUser={message.sender.username == user.username}
              key={message.message_id}
            />
          ))}
          <li className="invisible" key={"scrollToElement"} ref={myRef}></li>
        </ul>
      )}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          mutate({ message, sender });
        }}
        className="flex justify-between items-center p-4 w-full bg-blue-200">
        <input
          type="text"
          className="p-2 px-4 mx-3 w-full font-medium rounded-full focus:outline-none"
          placeholder="Type a message"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
        />
        <Svg onClick={() => mutate({ message, sender })} type="send" className="w-8 h-8 text-white bg-inherit" />
      </form>
    </motion.div>
  );
}

Message.propTypes = {
  message: PropTypes.object,
  toUser: PropTypes.bool,
  messageIndex: PropTypes.number,
};
function Message({ message, toUser, messageIndex }) {
  const sentDate = new Date(message.created_at);
  return (
    <motion.li
      initial={{ opacity: 0, x: toUser ? 100 : -100 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.25, delay: messageIndex * 0.1 }}
      className={` pl-2 py-1 w-fit rounded-md ${message.seen ? "bg-green-100" : "bg-blue-100"} ${toUser ? "ml-auto pr-2" : "pr-10"
        }`}>
      <p className={`break-all pt-1 font-medium ${toUser && "pl-1"}`}>{message.content}</p>
      <p className={`mt-0.5 text-xs font-light ${toUser && "text-right"}`}>{sentDate.toLocaleString()}</p>
    </motion.li>
  );
}

export default Inbox;
