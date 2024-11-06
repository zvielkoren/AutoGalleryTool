import React, { useState, useEffect } from 'react';

export function GalleryConfig() {
    const [config, setConfig] = useState({
        createThumbnails: false,
        organizeByDate: false,
        organizeByType: false,
        organizationPrompt: '',
        customPrompt: ''
    });

    const patterns = [
        {
            pattern: "{main}, {date:YYYY/MM}, {type}",
            description: "Basic - By Date and Type"
        },
        {
            pattern: "{main}, {date:YYYY}, {camera}, {custom:event_%name}",
            description: "Advanced - With Camera and Event"
        },
        {
            pattern: "{main}, {tags}, {date:YYYY-MM-DD}",
            description: "With Tags"
        }
    ];

    return (
        <div className="gallery-config">
            <section className="organization-pattern">
                <h2>Organization Pattern</h2>
                {patterns.map(({pattern, description}) => (
                    <button
                        onClick={() => setConfig({...config, organizationPrompt: pattern})}
                        key={description}
                    >
                        {description}
                    </button>
                ))}
                <input
                    type="text"
                    value={config.organizationPrompt}
                    onChange={(e) => setConfig({...config, organizationPrompt: e.target.value})}
                />
            </section>

            <section className="options">
                <label>
                    <input
                        type="checkbox"
                        checked={config.createThumbnails}
                        onChange={(e) => setConfig({...config, createThumbnails: e.target.checked})}
                    />
                    Create Thumbnails
                </label>
                {/* Add other options similarly */}
            </section>
        </div>
    );
}
