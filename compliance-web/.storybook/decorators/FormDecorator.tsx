import React from "react";
import { FormProvider, useForm } from "react-hook-form";
import { yupResolver } from "@hookform/resolvers/yup";
import * as yup from "yup";

// Default validation schema for stories
const defaultSchema = yup.object({
  textField: yup.string().optional(),
  switchField: yup.boolean().optional(),
  autocompleteField: yup.mixed().optional(),
  dateField: yup.date().optional(),
  checkboxField: yup.boolean().optional(),
  radioField: yup.string().optional(),
  toggleField: yup.string().optional(),
});

// Default form values
const defaultValues = {
  textField: "",
  switchField: false,
  autocompleteField: null,
  dateField: null,
  checkboxField: false,
  radioField: "",
  toggleField: "",
};

interface FormDecoratorProps {
  children: React.ReactNode;
  schema?: yup.ObjectSchema<any>;
  defaultFormValues?: Record<string, any>;
}

export const FormDecorator: React.FC<FormDecoratorProps> = ({
  children,
  schema = defaultSchema,
  defaultFormValues = defaultValues,
}) => {
  const methods = useForm({
    resolver: yupResolver(schema),
    defaultValues: defaultFormValues,
    mode: "onChange",
  });

  return (
    <FormProvider {...methods}>
      <form style={{ padding: "20px", maxWidth: "400px" }}>{children}</form>
    </FormProvider>
  );
};

// Higher-order component for easier usage in stories
export const withForm = (
  Component: React.ComponentType<any>,
  schema?: yup.ObjectSchema<any>,
  defaultFormValues?: Record<string, any>
) => {
  return (props: any) => (
    <FormDecorator schema={schema} defaultFormValues={defaultFormValues}>
      <Component {...props} />
    </FormDecorator>
  );
};
