import { FC } from "react";
import ControlledTextField from "@/components/Shared/Controlled/ControlledTextField";

const ContactForm: FC = () => {
  return (
    <>
      <ControlledTextField
        name="contactFullName"
        label="Full Name"
        fullWidth
      />
      <ControlledTextField
        name="contactTitle"
        label="Title"
        fullWidth
      />
      <ControlledTextField
        name="contactEmail"
        label="Email"
        placeholder="example@example.com"
        fullWidth
      />
      <ControlledTextField
        name="contactPhoneNumber"
        label="Phone Number"
        mask="(000) 000-0000"
        placeholder="(xxx) xxx-xxxx"
        fullWidth
      />
      <ControlledTextField
        name="contactComments"
        label="Comments"
        multiline
        fullWidth
      />
    </>
  );
};

export default ContactForm;
