import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';

export function FileProcessor() {
    const onDrop = useCallback(acceptedFiles => {
        // Handle file processing here
        const formData = new FormData();
        acceptedFiles.forEach(file => {
            formData.append('files', file);
        });

        fetch('/api/process', {
            method: 'POST',
            body: formData
        });
    }, []);

    const { getRootProps, getInputProps } = useDropzone({ onDrop });

    return (
        <div {...getRootProps()} className="dropzone">
            <input {...getInputProps()} />
            <p>Drag & drop images here, or click to select files</p>
        </div>
    );
}
