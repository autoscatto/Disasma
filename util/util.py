def getZeroTerminatedString(data, offset):
  string = []
  size   = 0
  while True:
    char = data[offset + size]
    if char == '\0':
      break

    string.append(char)
    size += 1

  return ''.join(string)
