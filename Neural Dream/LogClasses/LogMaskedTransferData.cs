namespace Neural_Style_Transfer.LogClasses
{
    class LogMaskedTransferData
    {
        public string Time { get; set; }
        public string ContentFilePath { get; set; }
        public string GeneratedFilePath { get; set; }
        public string MaskFilePath { get; set; }
        public string ParameterList { get; set; }
    }
}
