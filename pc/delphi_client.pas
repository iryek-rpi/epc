; Python client.py를 ChatGPT로 변환해서 테스트하지 못한 코드임

program CryptoClient;

{$APPTYPE CONSOLE}

uses
  SysUtils, WinSock;

const
  IP = '146.56.151.119';

var
  enc_socket, dec_socket: TSocket;

function InitConnection(port: Integer): TSocket;
var
  addr: sockaddr_in;
begin
  Result := INVALID_SOCKET;
  try
    enc_socket := socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if enc_socket = INVALID_SOCKET then
    begin
      WriteLn('Error creating socket');
      Exit;
    end;

    addr.sin_family := AF_INET;
    addr.sin_port := htons(port);
    addr.sin_addr.S_addr := inet_addr(PAnsiChar(IP));

    if connect(enc_socket, addr, SizeOf(addr)) = SOCKET_ERROR then
    begin
      CloseSocket(enc_socket);
      WriteLn('Error connecting ', IP, ':', port);
      Exit;
    end;
  except
    on E: Exception do
    begin
      WriteLn('Exception: ', E.Message);
      Exit;
    end;
  end;

  Result := enc_socket;
end;

function MakeMsg(const s: AnsiString; const token: TBytes): TBytes;
begin
  SetLength(Result, Length(token) + Length(s));
  Move(token[0], Result[0], Length(token));
  Move(s[1], Result[Length(token)], Length(s));
end;

function RequestTransform(const s: AnsiString; const token: TBytes;
  var crypto_socket: TSocket; port: Integer): AnsiString;
var
  msg, received: TBytes;
begin
  if crypto_socket = INVALID_SOCKET then
  begin
    crypto_socket := InitConnection(port);
    if crypto_socket = INVALID_SOCKET then
      Exit;
  end;

  msg := MakeMsg(s, token);
  send(crypto_socket, msg[0], Length(msg), 0);
  SetLength(received, 1024);
  recv(crypto_socket, received[0], 1024, 0);
  SetString(Result, PAnsiChar(received), StrLen(PAnsiChar(received)));
end;

var
  token: AnsiString;
  s, cipher, plain: AnsiString;
begin
  enc_socket := INVALID_SOCKET;
  dec_socket := INVALID_SOCKET;
  try
    while True do
    begin
      WriteLn(#10, '- ' + StringOfChar('*', 30));
      Write('Please input a token(1 byte): ');
      ReadLn(token);
      if Length(token) > 0 then
        SetLength(token, 1);

      Write('Please input a plain text: ');
      ReadLn(s);

      cipher := RequestTransform(s, TBytes(token), enc_socket, 8503);
      WriteLn('ciphertext received: ', cipher);

      plain := RequestTransform(cipher, TBytes(token), dec_socket, 8504);
      WriteLn('plaintext received: ', plain);
    end;
  finally
    if enc_socket <> INVALID_SOCKET then
      CloseSocket(enc_socket);
    if dec_socket <> INVALID_SOCKET then
      CloseSocket(dec_socket);
  end;
end.