import { useFormContext, Controller } from "react-hook-form";
import LexicalEditor from "@/components/Shared/LexicalEditor/LexicalEditor";
import { MentionData } from "@/components/Shared/LexicalEditor/LexicalUtils";
import { $generateHtmlFromNodes } from "@lexical/html";
import { $getRoot } from "lexical";
import { useMemo, useEffect, useState, useRef } from "react";
import { FormControl, FormHelperText } from "@mui/material";

interface ExtendedFieldErrors {
  html: {
    message: string;
    ref: string;
    type: string;
  };
  text: {
    message: string;
    ref: string;
    type: string;
  };
}

export default function ControlledLexicalEditor({
  name,
  label,
  placeholder = "Enter text...",
  isAdvanced = false,
  height,
  mentionsList,
  isRequired = false,
  disabled = false,
}: {
  name: string;
  label: string;
  placeholder?: string;
  isAdvanced?: boolean;
  height?: string;
  mentionsList?: MentionData[];
  isRequired?: boolean;
  disabled?: boolean;
}) {
  const {
    control,
    formState: { errors },
    watch,
  } = useFormContext();

  const [editorKey, setEditorKey] = useState<number>(0);
  const isUserTyping = useRef(false);
  const fieldValue = watch(name);

  // Effect to handle programmatic updates
  useEffect(() => {
    if (!isUserTyping.current && fieldValue?.html) {
      setEditorKey(prev => prev + 1);
    }
  }, [fieldValue?.html]);

  const errorMessage = useMemo(() => {
    const error = errors[name] as unknown as ExtendedFieldErrors;
    return error && error.text && error.text.message;
  }, [errors, name]);

  return (
    <FormControl fullWidth sx={{ marginBottom: "1.5rem" }}>
      <Controller
        name={name}
        control={control}
        render={({ field }) => (
          <>
            <LexicalEditor
              name={name}
              label={label}
              isAdvanced={isAdvanced}
              errorMsg={errorMessage}
              placeholder={placeholder}
              defaultHtml={field.value?.html}
              height={height}
              mentionsList={mentionsList}
              key={`lexical-editor-${name}-${editorKey}`}
              onChange={(editorState, editor) => {
                isUserTyping.current = true;
                editorState.read(() => {
                  const editorStateHtmlString = $generateHtmlFromNodes(editor);
                  const editorStateTextString = $getRoot()
                    .getTextContent()
                    ?.replace(/\n+/g, " ");
                  field.onChange({
                    html: editorStateHtmlString,
                    text: editorStateTextString,
                  });
                });
                // Reset the typing flag after a short delay
                setTimeout(() => {
                  isUserTyping.current = false;
                }, 100);
              }}
              isRequired={isRequired}
              disabled={disabled}
            />
            {errorMessage && (
              <FormHelperText
                error
                sx={{
                  fontSize: "0.875rem",
                  marginLeft: "0",
                }}
              >
                {errorMessage}
              </FormHelperText>
            )}
          </>
        )}
      />
    </FormControl>
  );
}
