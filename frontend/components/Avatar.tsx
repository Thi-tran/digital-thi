import Image from 'next/image';
import React from 'react';

interface AvatarProps {
  alt: string;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

const sizeMap = {
  sm: 'w-8 h-8',
  md: 'w-10 h-10',
  lg: 'w-12 h-12',
};

export const personalAvatar = '/profile.jpg';

export const Avatar: React.FC<AvatarProps> = ({
  alt,
  size = 'md',
  className = '',
}) => {
  return (
    <Image
      src={personalAvatar}
      alt={alt}
      className={`rounded-full object-cover ${sizeMap[size]} ${className}`}
      width={50}
      height={50}
    />
  );
};

export default Avatar;
