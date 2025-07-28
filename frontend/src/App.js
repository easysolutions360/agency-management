import React, { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Move FormInput component outside to prevent recreation on every render
const FormInput = ({ label, type = "text", value, onChange, required = true, options = null }) => (
  <div className="mb-4">
    <label className="block text-sm font-medium text-gray-700 mb-2">
      {label}
    </label>
    {options ? (
      <select
        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        value={value}
        onChange={onChange}
        required={required}
      >
        <option value="">Select {label}</option>
        {options.map((option, index) => (
          <option key={index} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    ) : (
      <input
        type={type}
        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        value={value}
        onChange={onChange}
        required={required}
      />
    )}
  </div>
);

// Move TabButton component outside to prevent recreation on every render
const TabButton = ({ tab, label, isActive, onClick }) => (
  <button
    className={`px-6 py-3 rounded-lg font-medium transition-colors ${
      isActive
        ? "bg-blue-600 text-white"
        : "bg-gray-200 text-gray-700 hover:bg-gray-300"
    }`}
    onClick={onClick}
  >
    {label}
  </button>
);

const App = () => {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [customers, setCustomers] = useState([]);
  const [projects, setProjects] = useState([]);
  const [dashboardProjects, setDashboardProjects] = useState([]);
  const [expiringDomains, setExpiringDomains] = useState([]);
  const [selectedProject, setSelectedProject] = useState(null);
  const [projectDomains, setProjectDomains] = useState([]);
  const [domains, setDomains] = useState([]);
  const [amcProjects, setAmcProjects] = useState([]);
  const [editingItem, setEditingItem] = useState(null);
  const [editingType, setEditingType] = useState(null);
  const [customerBalances, setCustomerBalances] = useState([]);
  const [selectedCustomer, setSelectedCustomer] = useState(null);
  const [customerLedger, setCustomerLedger] = useState([]);
  const [paymentModal, setPaymentModal] = useState(false);
  const [renewalModal, setRenewalModal] = useState(false);
  const [selectedDomain, setSelectedDomain] = useState(null);
  
  // Pagination states
  const [reportsTab, setReportsTab] = useState("customers");
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [searchTerm, setSearchTerm] = useState("");

  // Form states
  const [customerForm, setCustomerForm] = useState({
    name: "",
    phone: "",
    email: "",
    address: ""
  });

  const [projectForm, setProjectForm] = useState({
    customer_id: "",
    type: "",
    name: "",
    amount: "",
    start_date: "",
    end_date: ""
  });

  const [domainForm, setDomainForm] = useState({
    project_id: "",
    domain_name: "",
    hosting_provider: "",
    username: "",
    password: "",
    validity_date: "",
    renewal_amount: "",
    payment_type: "client"
  });

  const [paymentForm, setPaymentForm] = useState({
    customer_id: "",
    type: "",
    reference_id: "",
    amount: "",
    description: ""
  });

  const [renewalForm, setRenewalForm] = useState({
    new_validity_date: "",
    amount: "",
    payment_type: "client"
  });

  // API calls
  const fetchCustomers = async () => {
    try {
      const response = await axios.get(`${API}/customers`);
      setCustomers(response.data);
    } catch (error) {
      console.error("Error fetching customers:", error);
    }
  };

  const fetchProjects = async () => {
    try {
      const response = await axios.get(`${API}/projects`);
      setProjects(response.data);
    } catch (error) {
      console.error("Error fetching projects:", error);
    }
  };

  const fetchDashboardProjects = async () => {
    try {
      const response = await axios.get(`${API}/dashboard/projects`);
      setDashboardProjects(response.data);
    } catch (error) {
      console.error("Error fetching dashboard projects:", error);
    }
  };

  const fetchExpiringDomains = async () => {
    try {
      const response = await axios.get(`${API}/dashboard/expiring-domains`);
      setExpiringDomains(response.data);
    } catch (error) {
      console.error("Error fetching expiring domains:", error);
    }
  };

  const fetchDomains = async () => {
    try {
      const response = await axios.get(`${API}/domains`);
      setDomains(response.data);
    } catch (error) {
      console.error("Error fetching domains:", error);
    }
  };

  const fetchProjectDomains = async (projectId) => {
    try {
      const response = await axios.get(`${API}/domains/project/${projectId}`);
      setProjectDomains(response.data);
    } catch (error) {
      console.error("Error fetching project domains:", error);
    }
  };

  const fetchAmcProjects = async () => {
    try {
      const response = await axios.get(`${API}/dashboard/amc-projects`);
      setAmcProjects(response.data);
    } catch (error) {
      console.error("Error fetching AMC projects:", error);
    }
  };

  const fetchCustomerBalances = async () => {
    try {
      const response = await axios.get(`${API}/dashboard/customer-balances`);
      setCustomerBalances(response.data);
    } catch (error) {
      console.error("Error fetching customer balances:", error);
    }
  };

  const fetchCustomerLedger = async (customerId) => {
    try {
      const response = await axios.get(`${API}/ledger/customer/${customerId}`);
      setCustomerLedger(response.data);
    } catch (error) {
      console.error("Error fetching customer ledger:", error);
    }
  };

  useEffect(() => {
    fetchCustomers();
    fetchProjects();
    fetchDashboardProjects();
    fetchExpiringDomains();
    fetchDomains();
    fetchAmcProjects();
    fetchCustomerBalances();
  }, []);

  const handleCustomerSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/customers`, customerForm);
      setCustomerForm({ name: "", phone: "", email: "", address: "" });
      fetchCustomers();
      alert("Customer added successfully!");
    } catch (error) {
      console.error("Error adding customer:", error);
      alert("Error adding customer");
    }
  };

  const handleProjectSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/projects`, {
        ...projectForm,
        amount: parseFloat(projectForm.amount)
      });
      setProjectForm({
        customer_id: "",
        type: "",
        name: "",
        amount: "",
        start_date: "",
        end_date: ""
      });
      fetchProjects();
      fetchDashboardProjects();
      alert("Project added successfully!");
    } catch (error) {
      console.error("Error adding project:", error);
      alert("Error adding project");
    }
  };

  const handleDomainSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/domains`, domainForm);
      setDomainForm({
        project_id: "",
        domain_name: "",
        hosting_provider: "",
        username: "",
        password: "",
        validity_date: "",
        renewal_amount: "",
        payment_type: "client"
      });
      fetchDashboardProjects();
      fetchExpiringDomains();
      fetchDomains();
      if (selectedProject) {
        fetchProjectDomains(selectedProject);
      }
      alert("Domain/Hosting added successfully!");
    } catch (error) {
      console.error("Error adding domain:", error);
      alert("Error adding domain");
    }
  };

  const handlePaymentSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/payments`, paymentForm);
      setPaymentForm({
        customer_id: "",
        type: "",
        reference_id: "",
        amount: "",
        description: ""
      });
      setPaymentModal(false);
      fetchProjects();
      fetchDashboardProjects();
      fetchCustomerBalances();
      alert("Payment recorded successfully!");
    } catch (error) {
      console.error("Error recording payment:", error);
      alert("Error recording payment");
    }
  };

  const handleRenewalSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/domain-renewal/${selectedDomain.id}`, renewalForm);
      setRenewalForm({
        new_validity_date: "",
        amount: "",
        payment_type: "client"
      });
      setRenewalModal(false);
      setSelectedDomain(null);
      fetchDomains();
      fetchDashboardProjects();
      fetchExpiringDomains();
      fetchCustomerBalances();
      alert("Domain renewed successfully!");
    } catch (error) {
      console.error("Error renewing domain:", error);
      alert("Error renewing domain");
    }
  };

  const openPaymentModal = (customer_id, type, reference_id, description) => {
    setPaymentForm({
      customer_id,
      type,
      reference_id,
      amount: "",
      description
    });
    setPaymentModal(true);
  };

  const openRenewalModal = (domain) => {
    setSelectedDomain(domain);
    setRenewalModal(true);
  };

  // Delete functions
  const handleDeleteCustomer = async (customerId) => {
    if (window.confirm("Are you sure you want to delete this customer?")) {
      try {
        await axios.delete(`${API}/customers/${customerId}`);
        fetchCustomers();
        fetchDashboardProjects();
        alert("Customer deleted successfully!");
      } catch (error) {
        console.error("Error deleting customer:", error);
        alert("Error deleting customer");
      }
    }
  };

  const handleDeleteProject = async (projectId) => {
    if (window.confirm("Are you sure you want to delete this project?")) {
      try {
        await axios.delete(`${API}/projects/${projectId}`);
        fetchProjects();
        fetchDashboardProjects();
        fetchAmcProjects();
        alert("Project deleted successfully!");
      } catch (error) {
        console.error("Error deleting project:", error);
        alert("Error deleting project");
      }
    }
  };

  const handleDeleteDomain = async (domainId) => {
    if (window.confirm("Are you sure you want to delete this domain?")) {
      try {
        await axios.delete(`${API}/domains/${domainId}`);
        fetchDomains();
        fetchDashboardProjects();
        fetchExpiringDomains();
        alert("Domain deleted successfully!");
      } catch (error) {
        console.error("Error deleting domain:", error);
        alert("Error deleting domain");
      }
    }
  };

  // Edit functions
  const handleEditSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingType === "customer") {
        await axios.put(`${API}/customers/${editingItem.id}`, editingItem);
        fetchCustomers();
        fetchDashboardProjects();
      } else if (editingType === "project") {
        await axios.put(`${API}/projects/${editingItem.id}`, {
          ...editingItem,
          amount: parseFloat(editingItem.amount)
        });
        fetchProjects();
        fetchDashboardProjects();
        fetchAmcProjects();
      } else if (editingType === "domain") {
        await axios.put(`${API}/domains/${editingItem.id}`, editingItem);
        fetchDomains();
        fetchDashboardProjects();
        fetchExpiringDomains();
      }
      setEditingItem(null);
      setEditingType(null);
      alert("Updated successfully!");
    } catch (error) {
      console.error("Error updating:", error);
      alert("Error updating");
    }
  };

  const handleEditCancel = () => {
    setEditingItem(null);
    setEditingType(null);
  };

  // Pagination helper functions
  const getFilteredData = (data, searchTerm) => {
    if (!searchTerm) return data;
    return data.filter(item => 
      Object.values(item).some(value => 
        value.toString().toLowerCase().includes(searchTerm.toLowerCase())
      )
    );
  };

  const getPaginatedData = (data, currentPage, pageSize) => {
    if (pageSize === "all") return data;
    const startIndex = (currentPage - 1) * pageSize;
    const endIndex = startIndex + pageSize;
    return data.slice(startIndex, endIndex);
  };

  const getTotalPages = (totalItems, pageSize) => {
    if (pageSize === "all") return 1;
    return Math.ceil(totalItems / pageSize);
  };

  const handlePageChange = (newPage) => {
    setCurrentPage(newPage);
  };

  const handlePageSizeChange = (newPageSize) => {
    setPageSize(newPageSize);
    setCurrentPage(1);
  };

  const handleSearchChange = (newSearchTerm) => {
    setSearchTerm(newSearchTerm);
    setCurrentPage(1);
  };

  const handleReportsTabChange = (newTab) => {
    setReportsTab(newTab);
    setCurrentPage(1);
    setSearchTerm("");
  };

  // Pagination component
  const PaginationControls = ({ currentPage, totalPages, onPageChange, totalItems, pageSize, onPageSizeChange }) => (
    <div className="flex flex-col sm:flex-row justify-between items-center mt-6 space-y-4 sm:space-y-0">
      <div className="flex items-center space-x-4">
        <span className="text-sm text-gray-700">
          Showing {pageSize === "all" ? totalItems : Math.min(pageSize, totalItems)} of {totalItems} results
        </span>
        <div className="flex items-center space-x-2">
          <label className="text-sm text-gray-700">Show:</label>
          <select
            value={pageSize}
            onChange={(e) => onPageSizeChange(e.target.value === "all" ? "all" : parseInt(e.target.value))}
            className="px-2 py-1 border border-gray-300 rounded-md text-sm"
          >
            <option value={10}>10</option>
            <option value={50}>50</option>
            <option value={100}>100</option>
            <option value={500}>500</option>
            <option value={1000}>1000</option>
            <option value="all">All</option>
          </select>
        </div>
      </div>
      
      {pageSize !== "all" && totalPages > 1 && (
        <div className="flex items-center space-x-2">
          <button
            onClick={() => onPageChange(currentPage - 1)}
            disabled={currentPage === 1}
            className="px-3 py-1 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Previous
          </button>
          
          <div className="flex space-x-1">
            {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
              let pageNum;
              if (totalPages <= 5) {
                pageNum = i + 1;
              } else if (currentPage <= 3) {
                pageNum = i + 1;
              } else if (currentPage >= totalPages - 2) {
                pageNum = totalPages - 4 + i;
              } else {
                pageNum = currentPage - 2 + i;
              }
              
              return (
                <button
                  key={pageNum}
                  onClick={() => onPageChange(pageNum)}
                  className={`px-3 py-1 rounded-md ${
                    currentPage === pageNum
                      ? "bg-blue-600 text-white"
                      : "bg-gray-200 text-gray-700 hover:bg-gray-300"
                  }`}
                >
                  {pageNum}
                </button>
              );
            })}
          </div>
          
          <button
            onClick={() => onPageChange(currentPage + 1)}
            disabled={currentPage === totalPages}
            className="px-3 py-1 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Next
          </button>
        </div>
      )}
    </div>
  );

  const renderDashboard = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">Dashboard Overview</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-blue-50 p-4 rounded-lg">
            <h3 className="text-lg font-semibold text-blue-800">Total Customers</h3>
            <p className="text-3xl font-bold text-blue-600">{customers.length}</p>
          </div>
          <div className="bg-green-50 p-4 rounded-lg">
            <h3 className="text-lg font-semibold text-green-800">Total Projects</h3>
            <p className="text-3xl font-bold text-green-600">{projects.length}</p>
          </div>
          <div className="bg-red-50 p-4 rounded-lg">
            <h3 className="text-lg font-semibold text-red-800">Expiring Domains</h3>
            <p className="text-3xl font-bold text-red-600">{expiringDomains.length}</p>
          </div>
        </div>

        {expiringDomains.length > 0 && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <h3 className="text-lg font-semibold text-red-800 mb-3">⚠️ Domains Expiring Soon</h3>
            <div className="space-y-2">
              {expiringDomains.map((domain, index) => (
                <div key={index} className="bg-white p-3 rounded border">
                  <div className="flex justify-between items-center">
                    <div>
                      <p className="font-medium">{domain.domain_name}</p>
                      <p className="text-sm text-gray-600">
                        {domain.customer_name} - {domain.project_name}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm text-red-600 font-medium">
                        Expires: {new Date(domain.validity_date).toLocaleDateString()}
                      </p>
                      <p className="text-xs text-red-500">
                        {domain.days_remaining} days remaining
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="overflow-x-auto">
          <table className="w-full table-auto">
            <thead>
              <tr className="bg-gray-50">
                <th className="px-4 py-2 text-left">Customer</th>
                <th className="px-4 py-2 text-left">Project</th>
                <th className="px-4 py-2 text-left">Type</th>
                <th className="px-4 py-2 text-left">Amount</th>
                <th className="px-4 py-2 text-left">Duration</th>
                <th className="px-4 py-2 text-left">Domains</th>
              </tr>
            </thead>
            <tbody>
              {dashboardProjects.map((project) => (
                <tr key={project.id} className="border-b">
                  <td className="px-4 py-2">
                    <div>
                      <p className="font-medium">{project.customer_name}</p>
                      <p className="text-sm text-gray-600">{project.customer_email}</p>
                    </div>
                  </td>
                  <td className="px-4 py-2 font-medium">{project.name}</td>
                  <td className="px-4 py-2">{project.type}</td>
                  <td className="px-4 py-2">${project.amount.toLocaleString()}</td>
                  <td className="px-4 py-2">
                    <div className="text-sm">
                      <p>{new Date(project.start_date).toLocaleDateString()}</p>
                      <p>{new Date(project.end_date).toLocaleDateString()}</p>
                    </div>
                  </td>
                  <td className="px-4 py-2">
                    <div className="space-y-1">
                      {project.domains.map((domain, index) => (
                        <div key={index} className="text-sm">
                          <p className="font-medium">{domain.domain_name}</p>
                          <p className="text-gray-600">{domain.hosting_provider}</p>
                        </div>
                      ))}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );

  const renderCustomerForm = () => (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Add New Customer</h2>
      <form onSubmit={handleCustomerSubmit} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormInput
            label="Customer Name"
            value={customerForm.name}
            onChange={(e) => setCustomerForm({ ...customerForm, name: e.target.value })}
          />
          <FormInput
            label="Phone Number"
            type="tel"
            value={customerForm.phone}
            onChange={(e) => setCustomerForm({ ...customerForm, phone: e.target.value })}
          />
          <FormInput
            label="Email Address"
            type="email"
            value={customerForm.email}
            onChange={(e) => setCustomerForm({ ...customerForm, email: e.target.value })}
          />
          <FormInput
            label="Address"
            value={customerForm.address}
            onChange={(e) => setCustomerForm({ ...customerForm, address: e.target.value })}
          />
        </div>
        <button
          type="submit"
          className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors"
        >
          Add Customer
        </button>
      </form>
    </div>
  );

  const renderProjectForm = () => (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Add New Project</h2>
      <form onSubmit={handleProjectSubmit} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormInput
            label="Customer"
            value={projectForm.customer_id}
            onChange={(e) => setProjectForm({ ...projectForm, customer_id: e.target.value })}
            options={customers.map(customer => ({
              value: customer.id,
              label: `${customer.name} - ${customer.email}`
            }))}
          />
          <FormInput
            label="Project Type"
            value={projectForm.type}
            onChange={(e) => setProjectForm({ ...projectForm, type: e.target.value })}
          />
          <FormInput
            label="Project Name"
            value={projectForm.name}
            onChange={(e) => setProjectForm({ ...projectForm, name: e.target.value })}
          />
          <FormInput
            label="Project Amount"
            type="number"
            value={projectForm.amount}
            onChange={(e) => setProjectForm({ ...projectForm, amount: e.target.value })}
          />
          <FormInput
            label="Start Date"
            type="date"
            value={projectForm.start_date}
            onChange={(e) => setProjectForm({ ...projectForm, start_date: e.target.value })}
          />
          <FormInput
            label="End Date"
            type="date"
            value={projectForm.end_date}
            onChange={(e) => setProjectForm({ ...projectForm, end_date: e.target.value })}
            required={false}
          />
        </div>
        <button
          type="submit"
          className="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 transition-colors"
        >
          Add Project
        </button>
      </form>
    </div>
  );

  const renderDomainForm = () => (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Add Domain/Hosting</h2>
      <form onSubmit={handleDomainSubmit} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormInput
            label="Project"
            value={domainForm.project_id}
            onChange={(e) => setDomainForm({ ...domainForm, project_id: e.target.value })}
            options={projects.map(project => ({
              value: project.id,
              label: `${project.name} - ${project.type}`
            }))}
          />
          <FormInput
            label="Domain Name"
            value={domainForm.domain_name}
            onChange={(e) => setDomainForm({ ...domainForm, domain_name: e.target.value })}
          />
          <FormInput
            label="Hosting Provider"
            value={domainForm.hosting_provider}
            onChange={(e) => setDomainForm({ ...domainForm, hosting_provider: e.target.value })}
          />
          <FormInput
            label="Username"
            value={domainForm.username}
            onChange={(e) => setDomainForm({ ...domainForm, username: e.target.value })}
          />
          <FormInput
            label="Password"
            type="password"
            value={domainForm.password}
            onChange={(e) => setDomainForm({ ...domainForm, password: e.target.value })}
          />
          <FormInput
            label="Validity Date"
            type="date"
            value={domainForm.validity_date}
            onChange={(e) => setDomainForm({ ...domainForm, validity_date: e.target.value })}
          />
          <FormInput
            label="Renewal Amount"
            type="number"
            value={domainForm.renewal_amount}
            onChange={(e) => setDomainForm({ ...domainForm, renewal_amount: e.target.value })}
            required={false}
          />
          <FormInput
            label="Payment Type"
            value={domainForm.payment_type}
            onChange={(e) => setDomainForm({ ...domainForm, payment_type: e.target.value })}
            options={[
              { value: "client", label: "Client Pays" },
              { value: "agency", label: "Agency Pays" }
            ]}
          />
        </div>
        <button
          type="submit"
          className="w-full bg-purple-600 text-white py-2 px-4 rounded-md hover:bg-purple-700 transition-colors"
        >
          Add Domain/Hosting
        </button>
      </form>
    </div>
  );

  const renderReports = () => {
    // Get current data based on active reports tab
    let currentData = [];
    if (reportsTab === "customers") {
      currentData = customers;
    } else if (reportsTab === "projects") {
      currentData = projects;
    } else if (reportsTab === "domains") {
      currentData = domains;
    }

    // Apply search filter
    const filteredData = getFilteredData(currentData, searchTerm);
    
    // Apply pagination
    const paginatedData = getPaginatedData(filteredData, currentPage, pageSize);
    
    // Calculate total pages
    const totalPages = getTotalPages(filteredData.length, pageSize);

    return (
      <div className="space-y-6">
        {/* Payment Modal */}
        {paymentModal && (
          <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-md">
              <h3 className="text-lg font-bold mb-4">Record Payment</h3>
              <form onSubmit={handlePaymentSubmit} className="space-y-4">
                <FormInput
                  label="Amount"
                  type="number"
                  value={paymentForm.amount}
                  onChange={(e) => setPaymentForm({...paymentForm, amount: e.target.value})}
                />
                <FormInput
                  label="Description"
                  value={paymentForm.description}
                  onChange={(e) => setPaymentForm({...paymentForm, description: e.target.value})}
                />
                <div className="flex gap-2">
                  <button
                    type="submit"
                    className="flex-1 bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700"
                  >
                    Record Payment
                  </button>
                  <button
                    type="button"
                    onClick={() => setPaymentModal(false)}
                    className="flex-1 bg-gray-600 text-white py-2 px-4 rounded-md hover:bg-gray-700"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Renewal Modal */}
        {renewalModal && (
          <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-md">
              <h3 className="text-lg font-bold mb-4">Renew Domain: {selectedDomain?.domain_name}</h3>
              <form onSubmit={handleRenewalSubmit} className="space-y-4">
                <FormInput
                  label="New Validity Date"
                  type="date"
                  value={renewalForm.new_validity_date}
                  onChange={(e) => setRenewalForm({...renewalForm, new_validity_date: e.target.value})}
                />
                <FormInput
                  label="Renewal Amount"
                  type="number"
                  value={renewalForm.amount}
                  onChange={(e) => setRenewalForm({...renewalForm, amount: e.target.value})}
                />
                <FormInput
                  label="Payment Type"
                  value={renewalForm.payment_type}
                  onChange={(e) => setRenewalForm({...renewalForm, payment_type: e.target.value})}
                  options={[
                    { value: "client", label: "Client Paid" },
                    { value: "agency", label: "Agency Paid (Add to Customer Credit)" }
                  ]}
                />
                <div className="flex gap-2">
                  <button
                    type="submit"
                    className="flex-1 bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700"
                  >
                    Renew Domain
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setRenewalModal(false);
                      setSelectedDomain(null);
                    }}
                    className="flex-1 bg-gray-600 text-white py-2 px-4 rounded-md hover:bg-gray-700"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Edit Modal */}
        {editingItem && (
          <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-md">
              <h3 className="text-lg font-bold mb-4">Edit {editingType}</h3>
              <form onSubmit={handleEditSubmit} className="space-y-4">
                {editingType === "customer" && (
                  <>
                    <FormInput
                      label="Name"
                      value={editingItem.name}
                      onChange={(e) => setEditingItem({...editingItem, name: e.target.value})}
                    />
                    <FormInput
                      label="Phone"
                      value={editingItem.phone}
                      onChange={(e) => setEditingItem({...editingItem, phone: e.target.value})}
                    />
                    <FormInput
                      label="Email"
                      value={editingItem.email}
                      onChange={(e) => setEditingItem({...editingItem, email: e.target.value})}
                    />
                    <FormInput
                      label="Address"
                      value={editingItem.address}
                      onChange={(e) => setEditingItem({...editingItem, address: e.target.value})}
                    />
                  </>
                )}
                {editingType === "project" && (
                  <>
                    <FormInput
                      label="Type"
                      value={editingItem.type}
                      onChange={(e) => setEditingItem({...editingItem, type: e.target.value})}
                    />
                    <FormInput
                      label="Name"
                      value={editingItem.name}
                      onChange={(e) => setEditingItem({...editingItem, name: e.target.value})}
                    />
                    <FormInput
                      label="Amount"
                      type="number"
                      value={editingItem.amount}
                      onChange={(e) => setEditingItem({...editingItem, amount: e.target.value})}
                    />
                    <FormInput
                      label="Start Date"
                      type="date"
                      value={editingItem.start_date}
                      onChange={(e) => setEditingItem({...editingItem, start_date: e.target.value})}
                    />
                    <FormInput
                      label="End Date"
                      type="date"
                      value={editingItem.end_date || ""}
                      onChange={(e) => setEditingItem({...editingItem, end_date: e.target.value})}
                      required={false}
                    />
                  </>
                )}
                {editingType === "domain" && (
                  <>
                    <FormInput
                      label="Domain Name"
                      value={editingItem.domain_name}
                      onChange={(e) => setEditingItem({...editingItem, domain_name: e.target.value})}
                    />
                    <FormInput
                      label="Hosting Provider"
                      value={editingItem.hosting_provider}
                      onChange={(e) => setEditingItem({...editingItem, hosting_provider: e.target.value})}
                    />
                    <FormInput
                      label="Username"
                      value={editingItem.username}
                      onChange={(e) => setEditingItem({...editingItem, username: e.target.value})}
                    />
                    <FormInput
                      label="Password"
                      type="password"
                      value={editingItem.password}
                      onChange={(e) => setEditingItem({...editingItem, password: e.target.value})}
                    />
                    <FormInput
                      label="Validity Date"
                      type="date"
                      value={editingItem.validity_date}
                      onChange={(e) => setEditingItem({...editingItem, validity_date: e.target.value})}
                    />
                  </>
                )}
                <div className="flex gap-2">
                  <button
                    type="submit"
                    className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700"
                  >
                    Save
                  </button>
                  <button
                    type="button"
                    onClick={handleEditCancel}
                    className="flex-1 bg-gray-600 text-white py-2 px-4 rounded-md hover:bg-gray-700"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Reports Main Section */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6">
            <h2 className="text-2xl font-bold text-gray-800 mb-4 sm:mb-0">Reports</h2>
            
            {/* Search Bar */}
            <div className="w-full sm:w-auto">
              <input
                type="text"
                placeholder="Search..."
                value={searchTerm}
                onChange={(e) => handleSearchChange(e.target.value)}
                className="w-full sm:w-64 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          {/* Reports Tabs */}
          <div className="flex flex-wrap gap-2 mb-6">
            <button
              onClick={() => handleReportsTabChange("customers")}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                reportsTab === "customers"
                  ? "bg-blue-600 text-white"
                  : "bg-gray-200 text-gray-700 hover:bg-gray-300"
              }`}
            >
              Customers ({customers.length})
            </button>
            <button
              onClick={() => handleReportsTabChange("projects")}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                reportsTab === "projects"
                  ? "bg-blue-600 text-white"
                  : "bg-gray-200 text-gray-700 hover:bg-gray-300"
              }`}
            >
              Projects ({projects.length})
            </button>
            <button
              onClick={() => handleReportsTabChange("domains")}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                reportsTab === "domains"
                  ? "bg-blue-600 text-white"
                  : "bg-gray-200 text-gray-700 hover:bg-gray-300"
              }`}
            >
              Domains ({domains.length})
            </button>
          </div>

          {/* Table Content */}
          <div className="overflow-x-auto">
            {reportsTab === "customers" && (
              <table className="w-full table-auto">
                <thead>
                  <tr className="bg-gray-50">
                    <th className="px-4 py-2 text-left">Name</th>
                    <th className="px-4 py-2 text-left">Email</th>
                    <th className="px-4 py-2 text-left">Phone</th>
                    <th className="px-4 py-2 text-left">Address</th>
                    <th className="px-4 py-2 text-left">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {paginatedData.map((customer) => (
                    <tr key={customer.id} className="border-b hover:bg-gray-50">
                      <td className="px-4 py-2 font-medium">{customer.name}</td>
                      <td className="px-4 py-2">{customer.email}</td>
                      <td className="px-4 py-2">{customer.phone}</td>
                      <td className="px-4 py-2">{customer.address}</td>
                      <td className="px-4 py-2">
                        <div className="flex space-x-2">
                          <button
                            onClick={() => {
                              setEditingItem(customer);
                              setEditingType("customer");
                            }}
                            className="bg-blue-500 text-white px-2 py-1 rounded text-sm hover:bg-blue-600"
                          >
                            Edit
                          </button>
                          <button
                            onClick={() => handleDeleteCustomer(customer.id)}
                            className="bg-red-500 text-white px-2 py-1 rounded text-sm hover:bg-red-600"
                          >
                            Delete
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}

            {reportsTab === "projects" && (
              <table className="w-full table-auto">
                <thead>
                  <tr className="bg-gray-50">
                    <th className="px-4 py-2 text-left">Project Name</th>
                    <th className="px-4 py-2 text-left">Type</th>
                    <th className="px-4 py-2 text-left">Amount</th>
                    <th className="px-4 py-2 text-left">Paid</th>
                    <th className="px-4 py-2 text-left">Status</th>
                    <th className="px-4 py-2 text-left">Start Date</th>
                    <th className="px-4 py-2 text-left">End Date</th>
                    <th className="px-4 py-2 text-left">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {paginatedData.map((project) => (
                    <tr key={project.id} className="border-b hover:bg-gray-50">
                      <td className="px-4 py-2 font-medium">{project.name}</td>
                      <td className="px-4 py-2">{project.type}</td>
                      <td className="px-4 py-2">${project.amount.toLocaleString()}</td>
                      <td className="px-4 py-2">${(project.paid_amount || 0).toLocaleString()}</td>
                      <td className="px-4 py-2">
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          project.payment_status === "paid" 
                            ? "bg-green-100 text-green-800"
                            : project.payment_status === "partial"
                            ? "bg-yellow-100 text-yellow-800"
                            : "bg-red-100 text-red-800"
                        }`}>
                          {project.payment_status || "pending"}
                        </span>
                      </td>
                      <td className="px-4 py-2">{new Date(project.start_date).toLocaleDateString()}</td>
                      <td className="px-4 py-2">
                        {project.end_date ? new Date(project.end_date).toLocaleDateString() : "Not set"}
                      </td>
                      <td className="px-4 py-2">
                        <div className="flex space-x-2">
                          <button
                            onClick={() => {
                              setEditingItem(project);
                              setEditingType("project");
                            }}
                            className="bg-blue-500 text-white px-2 py-1 rounded text-sm hover:bg-blue-600"
                          >
                            Edit
                          </button>
                          <button
                            onClick={() => handleDeleteProject(project.id)}
                            className="bg-red-500 text-white px-2 py-1 rounded text-sm hover:bg-red-600"
                          >
                            Delete
                          </button>
                          {project.payment_status !== "paid" && (
                            <button
                              onClick={() => openPaymentModal(
                                project.customer_id, 
                                "project_advance", 
                                project.id, 
                                `Payment for ${project.name}`
                              )}
                              className="bg-green-500 text-white px-2 py-1 rounded text-sm hover:bg-green-600"
                            >
                              Add Payment
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}

            {reportsTab === "domains" && (
              <table className="w-full table-auto">
                <thead>
                  <tr className="bg-gray-50">
                    <th className="px-4 py-2 text-left">Domain Name</th>
                    <th className="px-4 py-2 text-left">Hosting Provider</th>
                    <th className="px-4 py-2 text-left">Username</th>
                    <th className="px-4 py-2 text-left">Validity Date</th>
                    <th className="px-4 py-2 text-left">Renewal Amount</th>
                    <th className="px-4 py-2 text-left">Status</th>
                    <th className="px-4 py-2 text-left">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {paginatedData.map((domain) => (
                    <tr key={domain.id} className="border-b hover:bg-gray-50">
                      <td className="px-4 py-2 font-medium">{domain.domain_name}</td>
                      <td className="px-4 py-2">{domain.hosting_provider}</td>
                      <td className="px-4 py-2">{domain.username}</td>
                      <td className="px-4 py-2">{new Date(domain.validity_date).toLocaleDateString()}</td>
                      <td className="px-4 py-2">${(domain.renewal_amount || 0).toLocaleString()}</td>
                      <td className="px-4 py-2">
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          domain.renewal_status === "renewed" 
                            ? "bg-green-100 text-green-800"
                            : domain.renewal_status === "due"
                            ? "bg-red-100 text-red-800"
                            : "bg-blue-100 text-blue-800"
                        }`}>
                          {domain.renewal_status || "active"}
                        </span>
                      </td>
                      <td className="px-4 py-2">
                        <div className="flex space-x-2">
                          <button
                            onClick={() => {
                              setEditingItem(domain);
                              setEditingType("domain");
                            }}
                            className="bg-blue-500 text-white px-2 py-1 rounded text-sm hover:bg-blue-600"
                          >
                            Edit
                          </button>
                          <button
                            onClick={() => handleDeleteDomain(domain.id)}
                            className="bg-red-500 text-white px-2 py-1 rounded text-sm hover:bg-red-600"
                          >
                            Delete
                          </button>
                          <button
                            onClick={() => openRenewalModal(domain)}
                            className="bg-green-500 text-white px-2 py-1 rounded text-sm hover:bg-green-600"
                          >
                            Renew
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>

          {/* Empty State */}
          {paginatedData.length === 0 && (
            <div className="text-center py-8">
              <p className="text-gray-500">
                {searchTerm ? "No results found for your search." : `No ${reportsTab} found.`}
              </p>
            </div>
          )}

          {/* Pagination Controls */}
          <PaginationControls
            currentPage={currentPage}
            totalPages={totalPages}
            onPageChange={handlePageChange}
            totalItems={filteredData.length}
            pageSize={pageSize}
            onPageSizeChange={handlePageSizeChange}
          />
        </div>
      </div>
    );
  };

  const renderAMC = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">AMC (Annual Maintenance Contract) Tracker</h2>
        <p className="text-gray-600 mb-6">
          This section shows projects that are due for AMC renewal (1 year after project completion)
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-blue-50 p-4 rounded-lg">
            <h3 className="text-lg font-semibold text-blue-800">Total AMC Due</h3>
            <p className="text-3xl font-bold text-blue-600">{amcProjects.length}</p>
          </div>
          <div className="bg-red-50 p-4 rounded-lg">
            <h3 className="text-lg font-semibold text-red-800">Overdue AMC</h3>
            <p className="text-3xl font-bold text-red-600">
              {amcProjects.filter(p => p.is_overdue).length}
            </p>
          </div>
          <div className="bg-green-50 p-4 rounded-lg">
            <h3 className="text-lg font-semibold text-green-800">Upcoming AMC</h3>
            <p className="text-3xl font-bold text-green-600">
              {amcProjects.filter(p => !p.is_overdue).length}
            </p>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full table-auto">
            <thead>
              <tr className="bg-gray-50">
                <th className="px-4 py-2 text-left">Project</th>
                <th className="px-4 py-2 text-left">Customer</th>
                <th className="px-4 py-2 text-left">Project End Date</th>
                <th className="px-4 py-2 text-left">AMC Due Date</th>
                <th className="px-4 py-2 text-left">Status</th>
                <th className="px-4 py-2 text-left">Contact</th>
              </tr>
            </thead>
            <tbody>
              {amcProjects.map((amcProject, index) => (
                <tr key={index} className="border-b">
                  <td className="px-4 py-2">
                    <div>
                      <p className="font-medium">{amcProject.project_name}</p>
                      <p className="text-sm text-gray-600">{amcProject.project_type}</p>
                      <p className="text-sm text-gray-600">${amcProject.project_amount.toLocaleString()}</p>
                    </div>
                  </td>
                  <td className="px-4 py-2">
                    <div>
                      <p className="font-medium">{amcProject.customer_name}</p>
                      <p className="text-sm text-gray-600">{amcProject.customer_email}</p>
                    </div>
                  </td>
                  <td className="px-4 py-2">
                    {new Date(amcProject.project_end_date).toLocaleDateString()}
                  </td>
                  <td className="px-4 py-2">
                    {new Date(amcProject.amc_due_date).toLocaleDateString()}
                  </td>
                  <td className="px-4 py-2">
                    <span className={`px-2 py-1 rounded text-sm font-medium ${
                      amcProject.is_overdue 
                        ? "bg-red-100 text-red-800" 
                        : amcProject.days_until_amc <= 7
                        ? "bg-yellow-100 text-yellow-800"
                        : "bg-green-100 text-green-800"
                    }`}>
                      {amcProject.is_overdue 
                        ? `Overdue by ${Math.abs(amcProject.days_until_amc)} days`
                        : amcProject.days_until_amc === 0
                        ? "Due Today"
                        : `Due in ${amcProject.days_until_amc} days`
                      }
                    </span>
                  </td>
                  <td className="px-4 py-2">
                    <div className="flex space-x-2">
                      <a
                        href={`tel:${amcProject.customer_phone}`}
                        className="bg-green-500 text-white px-2 py-1 rounded text-sm hover:bg-green-600"
                      >
                        Call
                      </a>
                      <a
                        href={`mailto:${amcProject.customer_email}`}
                        className="bg-blue-500 text-white px-2 py-1 rounded text-sm hover:bg-blue-600"
                      >
                        Email
                      </a>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          
          {amcProjects.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              <p>No AMC renewals due in the next 30 days</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-gray-800 mb-8">Agency Management System</h1>
        
        <div className="flex flex-wrap gap-4 mb-8">
          <TabButton
            tab="dashboard"
            label="Dashboard"
            isActive={activeTab === "dashboard"}
            onClick={() => setActiveTab("dashboard")}
          />
          <TabButton
            tab="customers"
            label="Add Customer"
            isActive={activeTab === "customers"}
            onClick={() => setActiveTab("customers")}
          />
          <TabButton
            tab="projects"
            label="Add Project"
            isActive={activeTab === "projects"}
            onClick={() => setActiveTab("projects")}
          />
          <TabButton
            tab="domains"
            label="Add Domain/Hosting"
            isActive={activeTab === "domains"}
            onClick={() => setActiveTab("domains")}
          />
          <TabButton
            tab="reports"
            label="Reports"
            isActive={activeTab === "reports"}
            onClick={() => setActiveTab("reports")}
          />
          <TabButton
            tab="amc"
            label="AMC Tracker"
            isActive={activeTab === "amc"}
            onClick={() => setActiveTab("amc")}
          />
          <TabButton
            tab="ledger"
            label="Customer Ledger"
            isActive={activeTab === "ledger"}
            onClick={() => setActiveTab("ledger")}
          />
        </div>

        {activeTab === "dashboard" && renderDashboard()}
        {activeTab === "customers" && renderCustomerForm()}
        {activeTab === "projects" && renderProjectForm()}
        {activeTab === "domains" && renderDomainForm()}
        {activeTab === "reports" && renderReports()}
        {activeTab === "amc" && renderAMC()}
      </div>
    </div>
  );
};

export default App;