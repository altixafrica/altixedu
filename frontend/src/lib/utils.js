export const cn = (...classes) => {
  return classes.filter(Boolean).join(' ');
};

export const classNames = (...args) => {
  return args
    .flat()
    .filter((x) => typeof x === 'string')
    .join(' ');
};
